# Runtime CPU

Nguồn: https://github.com/xinntao/Real-ESRGAN
Commit đã kiểm tra: a4abfb2979a7bbff3f69f58f58ae324608821e27.
RealESRGANer nhận device=torch.device('cpu'), half=False; worker ép CPU ngay cả máy có GPU.
Runtime đặt ngoài repo; không thêm submodule thứ hai trùng repo Colab đã có.

Cài bằng uv trong thư mục riêng:

```bash
git clone https://github.com/xinntao/Real-ESRGAN.git /path/realesrgan-runtime
git -C /path/realesrgan-runtime checkout a4abfb2979a7bbff3f69f58f58ae324608821e27
uv venv /path/realesrgan-env --python 3.12
uv pip install --python /path/realesrgan-env/bin/python torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu
uv pip install --python /path/realesrgan-env/bin/python 'numpy<2' 'opencv-python<4.12' basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8 tqdm
```

Tải hai file từ release chính thức v0.2.5.0 vào runtime/weights:
realesr-general-x4v3.pth, realesr-general-wdn-x4v3.pth.
Base URL: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/.
Worker thêm runtime vào sys.path, không cần pip setup.py develop.
Tạo file version bắt buộc bằng hàm upstream, chạy trong runtime với Python của môi trường riêng:
`python -c "import runpy; runpy.run_path('setup.py')['write_version_py']()"`.
BasicSR 1.4.2 import torchvision.transforms.functional_tensor đã bị bỏ; worker cung cấp alias
functional chứa rgb_to_grayscale trước import BasicSR. Không sửa site-packages.
FFmpeg/ffprobe phải có trong PATH. Model 4x general nhẹ hơn x4plus, không model anime.
Không dùng GFPGAN dù thư viện được cài làm dependency.
Mã Real-ESRGAN dùng BSD-3-Clause; kiểm tra giấy phép phụ thuộc khi phân phối.

Phiên cài đặt này: /workspace/scratch/c5ae3be9ac90/realesrgan-runtime và realesrgan-env.
Môi trường scratch có thể bị dọn; nếu mất thì chạy lại hướng dẫn, không tuyên bố còn cài sẵn.
