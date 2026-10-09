# Tiến độ bài lab Day22

Kiểm tra ngày 09/10/2026. Dataset riêng tư đã sẵn sàng; notebook chạy thử COMPLETE.

## Đã hoàn thành

- Điền ba câu hỏi ôn metric: True, False, True.
- Sửa thiết bị Re-ID thành torch.device và chạy detector trên thiết bị được chọn.
- Từ chối ảnh không đọc được để không bỏ frame âm thầm.
- Chuyển bản vá NumPy vào tiến trình TrackEval; stage theo split trong cấu hình.
- Tạo notebook Kaggle riêng tư, công cụ chuẩn bị dataset và pipeline thử/final.
- 31 unit test cục bộ passed; git diff --check passed.
- ZIP 678.839.577 byte, CRC hợp lệ, SHA-256:
  f7c727c5a7fdec471c6f9496b6ef384324148ccd7465c716505aa6ce1deff7f6.
- Đủ 4.137 ảnh: video_1=600, video_2=1050, video_3=837, video_4=900, video_5=750.
- Chia 41 phần nhỏ và ghép kiểm chứng: checksum toàn bộ khớp ZIP gốc.
- Notebook kiểm thử Kaggle phiên bản 3 COMPLETE trên Tesla T4.
- YOLO26n và năm tracker chạy thành công với ảnh tổng hợp.
- Script tracking đã xử lý năm ảnh thử bằng ByteTrack và BoT-SORT.
- TrackEval đã chấm dữ liệu tổng hợp thành công. Đây không phải điểm bài lab.

Notebook từ xa: https://www.kaggle.com/code/thngonquang/track4-day22-tracking-preflight

Bằng chứng địa phương:

- runs/kaggle_preflight_v3/day22/preflight.json
- runs/kaggle_preflight_v3/day22/trackeval_preflight_passed.txt
- runs/kaggle_preflight_v3/day22/preflight_trackeval.log
- runs/kaggle_preflight_v3/day22/versions.txt
- runs/kaggle_preflight_v3/track4-day22-tracking-preflight.log

## Đang thực hiện

Người dùng đã tải /home/conanwinner/Downloads/data_lab21.zip. ZIP và các bản
sao được giữ nguyên. Upload một tệp lớn bị truyền lại từ đầu; tiến trình đó đã
dừng khi chưa tạo dataset. Đã upload 41 phần và manifest bằng bốn kết nối,
xác minh đủ 42 tệp và trạng thái dataset ready.

Dataset: https://www.kaggle.com/datasets/thngonquang/track4-day22-tracking-lab-data

Notebook chính phiên bản 1 đã COMPLETE, đang tải đầu ra để kiểm tra:
https://www.kaggle.com/code/thngonquang/track4-day22-tracking

Gói gốc thiếu eval_config.json; script chấm dùng benchmark LAB, split train,
giữ nguyên gt.txt và seqinfo.ini. Không dùng nhãn cho bốn video còn lại.
Đang tải đầu ra lượt thử; chưa xác minh metric thật hoặc bản nộp đủ frame.

## Còn phải làm

1. Tải và kiểm chứng notebook ôn tập cùng 50 lượt thử đã chạy xong.
2. So sánh hai tracker và các cấu hình conf/iou trên mỗi video bằng preview.
3. Chọn cấu hình bằng bằng chứng thực tế rồi chạy đủ frame năm video.
4. Chấm video_1, điền báo cáo từ số liệu và quan sát, đóng gói năm txt + báo cáo.

Báo cáo mẫu chưa điền để tránh đưa nhận xét hoặc số liệu chưa quan sát vào bài.
Người dùng đã yêu cầu push code lên GitHub trước khi hoàn thiện kết quả.
Không đưa ảnh lab, trọng số hoặc video preview vào Git; không xóa dữ liệu.
