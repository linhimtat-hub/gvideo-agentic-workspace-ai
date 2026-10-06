"""Bounded-memory Real-ESRGAN CPU frame restoration, no face enhancer."""
import sys
from pathlib import Path
import subprocess
from fractions import Fraction
import time

runtime,source,output,sw,sh,tw,th,fps=sys.argv[1:]
sw,sh,tw,th=map(int,[sw,sh,tw,th])
sys.path.insert(0,runtime)
import torch
import torchvision.transforms.functional as functional
# BasicSR 1.4.2 references torchvision's removed module; rgb_to_grayscale
# is still provided by functional in torchvision 0.20.1.
sys.modules.setdefault('torchvision.transforms.functional_tensor',functional)
import cv2
import numpy as np
from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact

torch.set_num_threads(2)
model=SRVGGNetCompact(num_in_ch=3,num_out_ch=3,num_feat=64,num_conv=32,upscale=4,act_type='prelu')
weights=Path(runtime)/'weights'
up=RealESRGANer(scale=4,model=model,model_path=[str(weights/'realesr-general-x4v3.pth'),
 str(weights/'realesr-general-wdn-x4v3.pth')],dni_weight=[0.2,0.8],tile=128,tile_pad=10,
 half=False,device=torch.device('cpu'))
dec=subprocess.Popen(['ffmpeg','-v','error','-i',source,'-map','0:v:0','-fps_mode','passthrough',
 '-f','rawvideo','-pix_fmt','bgr24','pipe:1'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','bgr24','-s',f'{tw}x{th}',
 '-r',fps,'-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18',
 '-pix_fmt','yuv420p',output],stdin=subprocess.PIPE)
count=0; started=time.time()
try:
 while True:
  buffer=bytearray()
  while len(buffer)<sw*sh*3:
   piece=dec.stdout.read(sw*sh*3-len(buffer))
   if not piece: break
   buffer.extend(piece)
  if not buffer: break
  if len(buffer)!=sw*sh*3: raise RuntimeError('Frame chưa đủ dữ liệu')
  image=np.frombuffer(buffer,dtype=np.uint8).reshape(sh,sw,3)
  # Model restores 4x; final Lanczos fit preserves the complete source frame.
  restored,_=up.enhance(image,outscale=4)
  scale=min(tw/sw,th/sh); w,h=round(sw*scale),round(sh*scale)
  resized=cv2.resize(restored,(w,h),interpolation=cv2.INTER_LANCZOS4)
  canvas=np.zeros((th,tw,3),dtype=np.uint8)
  x,y=(tw-w)//2,(th-h)//2; canvas[y:y+h,x:x+w]=resized
  enc.stdin.write(canvas.tobytes()); count+=1
  print(f'frame={count} elapsed={time.time()-started:.1f}s',flush=True)
 enc.stdin.close()
 assert dec.wait()==0,'Decode failed'
 assert enc.wait()==0,'Encode failed'
 assert count>0,'No frames'
except BaseException:
 dec.kill(); enc.kill(); dec.wait(); enc.wait(); raise
print(f'PASS CPU: {count} frames, {time.time()-started:.1f}s',flush=True)
