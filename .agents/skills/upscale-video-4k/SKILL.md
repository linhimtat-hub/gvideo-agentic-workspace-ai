---
name: upscale-video-4k
description: Upscale video lên 4K local bằng CPU, dùng Real-ESRGAN phục hồi chi tiết hoặc FFmpeg Lanczos phóng lớn nhanh. Dùng khi người dùng tải video và yêu cầu upscale 4K không dùng GPU/Colab, giữ mặt thật, FPS và âm thanh.
---

# Upscale video 4K CPU

Đọc AGENTS.md. Cài runtime riêng ngoài workspace theo [runtime.md](references/runtime.md).
Không upload media lên Google. Mặc định AI CPU dùng model general, denoise 0.2, không face enhancer.
Phân biệt AI phục hồi chi tiết với Lanczos chỉ phóng lớn; không tuyên bố tương đương nguồn 4K gốc.

Chạy script từ gốc workspace bằng uv run --script, thử --thu trước:

```bash
uv run --script .agents/skills/upscale-video-4k/scripts/upscale.py --input /path/video.mp4 --output outputs/<du-an>/<luot-moi>/video-4k.mp4 --mode ai --python /path/realesrgan-env/bin/python --runtime /path/realesrgan-runtime --thu
```

--thu chỉ kiểm tra đầu vào/kích thước và dựng kế hoạch, không xác nhận dependencies/model đã chạy.
Bỏ --thu để render; dùng --mode lanczos nếu cần xuất nhanh không cài model/PyTorch.
AI cần video CFR, pixel vuông và không metadata xoay; script báo lỗi nếu chưa chuẩn hóa.
Không tự chuyển VFR thành CFR khi người dùng yêu cầu giữ timing.
Đầu ra ngang 3840×2160, dọc 2160×3840, vuông 2160×2160; thêm viền khi lệch tỷ lệ,
không crop khung hình. Giữ FPS, không nội suy 60 fps. Audio đầu tiên được mã hóa AAC 192k,
không hứa bitstream âm thanh giữ nguyên. Không nâng HDR: pipeline này xuất SDR 8-bit.
Với nguồn HDR cần hỏi/chọn workflow giữ HDR trước, không chạy pipeline này.

CPU AI có thể rất chậm cho video dài; chạy mẫu ngắn đại diện để đo trước.
Mẫu cài đặt nhỏ chỉ chứng minh pipeline hoạt động, không suy ra tốc độ/chất lượng clip cưới.
Giữ media gốc; chọn output mới dưới outputs/. Không chép media vào inputs/.
Đọc RUN.json và process.log. Chỉ gửi output sau status succeeded và kiểm tra mặt/nhấp nháy;
khi cần xem nội dung video dùng phan-tich-video theo quy tắc workspace.
Nếu lỗi, giữ log và báo thực tế; không đổi sang Lanczos rồi gọi đó là AI.
