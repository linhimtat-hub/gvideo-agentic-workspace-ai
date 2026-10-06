#!/usr/bin/env python3
"""Open pinned CatVTON locally with a separately installed runtime."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--precision', choices=['no', 'fp16', 'bf16'], default='fp16')
    parser.add_argument('--thu', action='store_true')
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[4]
    runtime = workspace / 'external' / 'CatVTON'
    output = Path(args.output_dir).resolve()
    if not (runtime / 'app.py').is_file():
        parser.error('Thiếu submodule: chạy git submodule update --init --recursive')
    if not output.is_relative_to(workspace / 'outputs'):
        parser.error('--output-dir phải nằm dưới outputs/ của workspace')
    if output.exists():
        parser.error('Chọn thư mục đầu ra mới để giữ kết quả cũ')
    bootstrap = (
        "import gradio as gr, runpy, sys; "
        "original = gr.Blocks.launch; "
        "gr.Blocks.launch = lambda self,*a,**k: original(self,*a,"
        "**dict(k,share=False,server_name='127.0.0.1')); "
        "sys.argv = ['app.py'] + sys.argv[1:]; "
        "runpy.run_path('app.py',run_name='__main__')"
    )
    command = [args.python, '-c', bootstrap, '--output_dir', str(output),
               '--mixed_precision', args.precision, '--repaint']
    print(json.dumps({'runtime': str(runtime), 'output': str(output),
                      'command': command, 'dry_run': args.thu}, ensure_ascii=False), flush=True)
    if args.thu:
        return 0
    check = subprocess.run([args.python, '-c',
                            "import torch; assert torch.cuda.is_available(), 'Cần GPU NVIDIA/CUDA'"],
                           cwd=runtime)
    if check.returncode:
        return check.returncode
    output.mkdir(parents=True)
    with (output / 'RUN.json').open('w') as log:
        json.dump({'backend': 'CatVTON', 'command': command, 'status': 'app-starting'}, log)
    return subprocess.run(command, cwd=runtime).returncode


if __name__ == '__main__':
    sys.exit(main())
