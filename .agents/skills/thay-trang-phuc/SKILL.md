---
name: thay-trang-phuc
description: Thay trang phục theo ảnh mẫu bằng CatVTON local và chuẩn bị video try-on với CatV2TON. Dùng khi yêu cầu đổi váy cưới, áo dài, vest, mặc trang phục mẫu hoặc virtual try-on; không dùng thay mặt hoặc chỉ đổi màu áo.
---

# Thay trang phục

Đọc AGENTS.md. Dùng repo chính thức cố định commit bằng git submodule:
external/CatVTON cho ảnh, external/CatV2TON cho video.
Chạy `git submodule update --init --recursive` nếu thiếu code.
Đọc [runtime.md](references/runtime.md) trước khi thiết lập môi trường hoặc xử lý video.

## Ảnh

Chuẩn bị ảnh người và ảnh trang phục rõ. Xác định đúng người khi có nhiều người.
Ưu tiên giữ mặt thật, góc mặt, tay, tóc và bối cảnh; mask chỉ phủ trang phục.
Không hứa giữ mặt 100%; kiểm tra kết quả, dùng swap-guong-mat để phục hồi mặt khi cần.
Cài runtime riêng ngoài workspace theo README CatVTON; cần CUDA, checkpoint và dependencies.
Không pip install vào workspace gvideo. Chạy thử, rồi bỏ --thu để mở app localhost:

```bash
uv run --script .agents/skills/thay-trang-phuc/scripts/launch_tryon.py --python /opt/catvton-env/bin/python --output-dir outputs/<du-an>/<luot-moi>/tryon --thu
```

App nhận ảnh người, ảnh đồ, loại đồ và mask; không phải CLI tự render từ hai file.
Chọn upper/lower/overall phù hợp. Kiểm tra mask không chạm mắt, miệng hoặc tóc.
Lưu ảnh kết quả vào output mới. Mở app thành công không có nghĩa là đã tạo ảnh.
App tự lưu bảng so sánh bốn ảnh; chọn "result only" và tải ảnh kết quả riêng từ UI.
Nếu không có công cụ tương tác với app, báo giới hạn đó, không tuyên bố đã thay đồ.

## Video

CatV2TON cung cấp script cho dataset ViViD/VVT, không nhận trực tiếp --video clip.mp4.
Chuẩn bị frame/video, trang phục, mask và DensePose theo loader ở commit cố định.
Đối chiếu định dạng trước khi chạy; clip hai người không tương đương dataset một người.
Thử đoạn ngắn, kiểm tra nhấp nháy, mặt và tay. Khi cần xem nội dung, dùng phan-tich-video.
Giữ FPS/thời lượng và ghép lại âm thanh nguồn sau render; kiểm tra ffprobe trước khi gửi.
Upstream CatV2TON ghi cứng 24 fps: sửa bước xuất để dùng FPS nguồn trước khi render,
không ghép audio 30 fps vào file 24 fps rồi tuyên bố giữ thời lượng.
Không dùng CatVTON render độc lập từng frame rồi tuyên bố video nhất quán theo thời gian.

## Trạng thái và giấy phép

Phân biệt đã thêm code, đã cài runtime/model, đã render mẫu và đã kiểm tra thành phẩm.
Không có GPU thì chỉ báo tích hợp code hoàn tất, chưa sẵn sàng render local.
CatVTON ghi CC BY-NC-SA 4.0, không mặc định dùng cho dịch vụ ảnh cưới thương mại.
CatV2TON không có LICENSE ở commit cố định; xác minh quyền code/model trước dùng thương mại.
