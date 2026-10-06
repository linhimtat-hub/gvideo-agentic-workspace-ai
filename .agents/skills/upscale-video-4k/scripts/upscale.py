#!/usr/bin/env python3
"""CPU-only 4K video export. AI runtime is installed outside the workspace."""
import argparse
from fractions import Fraction
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def probe(path, frames=False):
    cmd=['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]
    if frames:
        cmd[3:3]=['-count_frames']
    return json.loads(subprocess.check_output(cmd))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--mode',choices=['ai','lanczos'],default='ai')
    p.add_argument('--python',default=os.environ.get('REALESRGAN_PYTHON'))
    p.add_argument('--runtime',default=os.environ.get('REALESRGAN_DIR'))
    p.add_argument('--thu',action='store_true')
    a=p.parse_args()
    source=Path(a.input).resolve(); out=Path(a.output).resolve()
    root=Path(__file__).resolve().parents[4]
    if not source.is_file(): p.error('Không thấy video đầu vào')
    if out.suffix.lower()!='.mp4' or not out.is_relative_to(root/'outputs'):
        p.error('Chọn .mp4 mới dưới outputs/ của workspace')
    if out.exists(): p.error('Không ghi đè video đã có')
    info=probe(source); v=next((s for s in info['streams'] if s['codec_type']=='video'),None)
    if not v: p.error('Không có video stream')
    if v.get('color_transfer') in ['smpte2084','arib-std-b67']:
        p.error('Nguồn HDR cần workflow giữ HDR/tone-map riêng')
    if v.get('sample_aspect_ratio','1:1') not in ['1:1','N/A']:
        p.error('Cần chuẩn hóa sample aspect ratio trước')
    if any(abs(s.get('rotation',0))>0 for s in v.get('side_data_list',[])):
        p.error('Cần chuẩn hóa metadata xoay trước')
    width,height=v['width'],v['height']
    target=(2160,3840) if height>width else (3840,2160)
    if width==height: target=(2160,2160)
    fps=Fraction(v.get('avg_frame_rate','0/1'))
    if fps<=0: p.error('Không xác định được FPS')
    cfg={'source':str(source),'output':str(out),'mode':a.mode,'size':target,
         'fps':str(fps),'runtime':a.runtime,'python':a.python}
    print(json.dumps(cfg,ensure_ascii=False),flush=True)
    if a.thu: return 0
    if a.mode=='ai':
        if not a.python or not a.runtime: p.error('AI cần --python và --runtime riêng')
        rt=Path(a.runtime).resolve()
        if not (rt/'realesrgan/utils.py').is_file(): p.error('Runtime Real-ESRGAN chưa cài')
        for name in ['realesr-general-x4v3.pth','realesr-general-wdn-x4v3.pth']:
            if not (rt/'weights'/name).is_file(): p.error('Thiếu model '+name)
        # Frame-by-frame inference requires constant timing; do not silently flatten VFR.
        data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
             '-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(source)]))
        ts=[float(f['best_effort_timestamp_time']) for f in data['frames'] if 'best_effort_timestamp_time' in f]
        if any(abs((b-c)-1/float(fps))>0.0015 for c,b in zip(ts,ts[1:])):
            p.error('Video VFR: dùng lanczos để giữ timing hoặc chuẩn hóa CFR trước')
    run=out.parent/(out.stem+'-run')
    if run.exists(): p.error('Thư mục run đã có, chọn tên output mới')
    run.mkdir(parents=True)
    tmp=run/'complete.mp4'
    cfg.update(status='running',started=time.time())
    log=run/'RUN.json'; log.write_text(json.dumps(cfg,indent=2))
    tw,th=target
    vf=f'scale={tw}:{th}:force_original_aspect_ratio=decrease:flags=lanczos,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2,setsar=1'
    try:
        with (run/'process.log').open('w') as stream:
            if a.mode=='ai':
                worker=Path(__file__).with_name('ai_worker.py')
                video=run/'ai-video.mp4'
                subprocess.run([a.python,str(worker),str(rt),str(source),str(video),str(width),str(height),
                                str(tw),str(th),str(fps)],check=True,stdout=stream,stderr=stream)
                cmd=['ffmpeg','-v','error','-n','-i',str(video),'-i',str(source),'-map','0:v:0','-map','1:a:0?',
                     '-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(tmp)]
            else:
                cmd=['ffmpeg','-v','error','-n','-i',str(source),'-map','0:v:0','-map','0:a:0?',
                     '-vf',vf,'-fps_mode','passthrough','-c:v','libx264','-threads','2','-preset','medium',
                     '-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(tmp)]
            subprocess.run(cmd,check=True,stdout=stream,stderr=stream)
        result=probe(tmp,True); ov=next(s for s in result['streams'] if s['codec_type']=='video')
        assert (ov['width'],ov['height'])==target,'Sai kích thước'
        assert Fraction(ov['avg_frame_rate'])==fps,'Sai FPS'
        assert abs(float(result['format']['duration'])-float(info['format']['duration']))<0.1,'Sai thời lượng'
        assert int(ov['nb_read_frames'])>0,'Không giải mã được frame'
        if a.mode=='ai':
            assert int(ov['nb_read_frames'])==len(ts),'Sai số frame'
        assert any(s['codec_type']=='audio' for s in result['streams'])==any(s['codec_type']=='audio' for s in info['streams']),'Thiếu audio'
        os.replace(tmp,out)
        cfg.update(status='succeeded',result=result,elapsed=time.time()-cfg['started'])
        log.write_text(json.dumps(cfg,indent=2))
        print('PASS:',out,flush=True)
        return 0
    except Exception as e:
        cfg.update(status='failed',error=str(e)); log.write_text(json.dumps(cfg,indent=2))
        print(f'Lỗi: {e}. Xem {run}/process.log',file=sys.stderr)
        return 1


if __name__=='__main__':
    sys.exit(main())
