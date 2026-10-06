# Runtime và định dạng

## Ảnh — CatVTON

Nguồn: https://github.com/Zheng-Chong/CatVTON
Commit: 7818397f25613beedb3d861a34769f607cfcf3b1.
README hướng dẫn Python 3.9, cài requirements.txt trong môi trường riêng ngoài workspace.
App dùng CUDA; tác giả báo khoảng 8 GB VRAM ở 1024×768 với bf16.
bf16 cần GPU hỗ trợ; launcher mặc định fp16.
Model nền, CatVTON và model mask được tải từ Hugging Face ở lần chạy đầu.
Dry-run không tải model. Upstream bật share=True; launcher ép share=False và bind localhost.
Không commit media người dùng hoặc checkpoint.

## Video — CatV2TON

Nguồn: https://github.com/Zheng-Chong/CatV2TON
Commit: d8abdab93c9e3ffc89f6f9e13dbbee6b88e85cfc.
Model mặc định: alibaba-pai/EasyAnimateV4-XL-2-InP, zhengchong/CatV2TON, zhengchong/CatVTON.
Repo không có requirements.txt/cài đặt hoàn chỉnh ở commit này.
Đối chiếu imports, EasyAnimate và CUDA trước khi cài; requirements CatVTON không đủ chứng minh
CatV2TON đã cài thành công.

Lệnh chính thức cần dataset đã chuẩn bị (chạy từ external/CatV2TON):

```bash
/opt/catv2ton-env/bin/python eval_video_try_on.py --dataset vivid --data_root_path /data/ViViD-S-Test --output_dir /absolute/workspace/outputs/<du-an>/<luot-moi>/video --batch_size 1 --seed 42 --mixed_precision bf16 --repaint
```

Đọc VividTestDataset/VVTTestDataset trong eval_video_try_on.py để dựng manifest/đường dẫn.
ViViD cần test_data_180[_unpaired].jsonl và front_seqs. Tạo dataset dẫn xuất riêng:
loader có thể ghi mask vào data_root_path, không trỏ vào media gốc của người dùng.
VVT dùng test_person_clothes_pose_tuple.txt, lip_clothes_person, test_frames,
test_densepose-magcianimate và test_agn_mask_new. Kiểm tra mask thực tế với đồ cưới.
Audio không được pipeline try-on đảm bảo; ghép nguồn sau khi kiểm tra số frame/FPS.
eval_video_try_on.py ghi write_video(..., fps=24); cần adapter/sửa xuất FPS trước sản xuất.
ViViD loader có nhánh lỗi dùng self.missing_files chưa khai báo; kiểm tra đủ file trước chạy.
Xác minh giấy phép code/model nền và phụ thuộc trước dùng thương mại.
