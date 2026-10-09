# Tiến độ bài lab Day22

Kiểm tra ngày 09/10/2026: **SẴN SÀNG NỘP**. Làm cá nhân:
Đoàn Quang Thắng — MSSV 2A202602395.

## Kết quả đã xác minh

- Dataset riêng tư đã ready, đủ 41 phần và manifest (42 tệp).
- ZIP gốc 678.839.577 byte, CRC hợp lệ; ghép lại trên Kaggle khớp SHA-256
  f7c727c5a7fdec471c6f9496b6ef384324148ccd7465c716505aa6ce1deff7f6.
- Đủ 4.137 ảnh: video_1=600, video_2=1050, video_3=837,
  video_4=900, video_5=750. Chỉ video_1 có nhãn.
- Preflight phiên bản 3 COMPLETE; detector, năm tracker và TrackEval
  chạy thành công trên dữ liệu tổng hợp để kiểm tra môi trường.
- Notebook chính phiên bản 1 COMPLETE: 50 lượt thử, 8.400 frame xử lý;
  toàn bộ MOT và log đúng số frame. Hai baseline video_1 chấm đủ 600 frame.
- Notebook chính phiên bản 2 COMPLETE: bản cuối đủ 4.137 frame, Tesla T4.
- Notebook ôn tập thực thi trên ảnh lab thật; cả ba câu đúng.
- 31 unit test đạt ở máy cục bộ và Kaggle; git diff --check đạt.
- Kiểm tra trực quan cùng frame giữa hai tracker, các ngưỡng conf/iou;
  kiểm tra thêm ba frame giữa/cuối trên mỗi video của bản đầy đủ.
- Năm preview được ffprobe đếm đúng số ảnh gốc; năm file MOT hợp lệ.
- Báo cáo điền đủ cấu hình, phương án loại, metric, phân tích và lỗi còn lại.
- Gói nộp đã tạo bằng script kiểm tra, trạng thái SẴN SÀNG NỘP.

| Video | Tracker | conf | iou | Frame | Dòng MOT |
|---|---|---:|---:|---:|---:|
| video_1 | BoT-SORT | 0,30 | 0,50 | 600 | 4.582 |
| video_2 | BoT-SORT | 0,15 | 0,50 | 1.050 | 13.821 |
| video_3 | BoT-SORT | 0,15 | 0,50 | 837 | 5.043 |
| video_4 | BoT-SORT | 0,30 | 0,50 | 900 | 6.220 |
| video_5 | ByteTrack | 0,30 | 0,50 | 750 | 2.028 |

Video_1 bản cuối: HOTA 29,460; MOTA 19,811; IDF1 29,354 (phần trăm).
Không có số metric cho video_2–video_5. Gói giảng viên thiếu
`eval_config.json`; dùng tên chấm chung LAB/train, giữ nguyên nhãn và seqinfo.

## Đầu ra và bằng chứng

- Gói nộp: `submission/Day22_DoanQuangThang_2A202602395.zip`.
- Báo cáo: `submission_template/BAO_CAO_mau.md`.
- Lựa chọn và thử nghiệm: `kaggle/selections.json`, `kaggle/THU_NGHIEM.md`.
- Đầu ra thử: `runs/kaggle_trials_v1/day22/`.
- Đầu ra cuối, notebook ôn tập đã chạy và video: `runs/kaggle_final_v2/day22/`.
- Bản tải riêng tệp nhẹ: `runs/kaggle_final_v2_text/day22/`.
- Ảnh kiểm tra trực quan: `runs/inspection/`.
- ZIP có `KIEM_TRA.json`, log metric, phiên bản thư viện, thông tin GPU,
  checksum trọng số, cấu hình và commit TrackEval.

Dataset: https://www.kaggle.com/datasets/thngonquang/track4-day22-tracking-lab-data

Notebook chính: https://www.kaggle.com/code/thngonquang/track4-day22-tracking

Preflight: https://www.kaggle.com/code/thngonquang/track4-day22-tracking-preflight

Code đã push lên GitHub trước theo yêu cầu, commit `c9a867b`.
Bản hoàn chỉnh gồm báo cáo, lựa chọn và gói nộp được push tiếp sau kiểm tra.
ZIP tải gốc và mọi bản sao giữ nguyên; không xóa dữ liệu.
Ảnh lab, trọng số và video preview không được đưa vào Git.
