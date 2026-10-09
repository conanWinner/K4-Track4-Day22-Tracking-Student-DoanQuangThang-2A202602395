# Đối chiếu yêu cầu lab lần cuối

Ngày kiểm tra: 09/10/2026. Đối chiếu trực tiếp với `HUONG_DAN.md`, code,
snapshot notebook Kaggle, log thực thi và nội dung ZIP hiện tại.
**Kết luận: đáp ứng các yêu cầu bắt buộc của quy trình và hồ sơ nộp.**
Chất lượng tracking còn lỗi; không suy ra điểm chấm của giảng viên từ việc
các kiểm tra định dạng và quy trình đạt.

| Yêu cầu trong đề | Bằng chứng đã kiểm tra | Kết quả |
|---|---|---|
| Detector `yolo26n.pt`, ảnh 640, lớp người 0, Re-ID `osnet_x0_25_msmt17.pt` giữ nguyên | So hằng số với commit ban đầu `dd4aa04`; so script hiện tại với snapshot trong notebook đã dùng cho bản đầy đủ; log nạp mô hình và checksum trọng số được lưu | Đạt |
| Mỗi video có một tracker chuyển động và một tracker có Re-ID | Manifest và đầu ra thật: đủ ByteTrack và BoT-SORT trên cả năm video, tổng 50 lượt | Đạt |
| Thử conf 0,15/0,30/0,50 và iou 0,40/0,50/0,70, mỗi lần đổi một tham số | Mỗi tracker/mỗi video đủ năm cặp `(0.30,0.50)`, `(0.15,0.50)`, `(0.50,0.50)`, `(0.30,0.40)`, `(0.30,0.70)`; kiểm tra từng file MOT và log | Đạt |
| Hoàn thành notebook ôn metric và chạy YOLO trên ảnh thật | Notebook đã thực thi không có ô lỗi, đúng ba câu, có output ảnh `000001.jpg` và số hộp người ở ba mức conf | Đạt |
| Bản chính thức chạy đủ frame trên ảnh `img1`, không giới hạn thử | Snapshot nhánh final bỏ `--max-frames`; số ảnh, log và số frame preview khớp từng video | Đạt |
| Năm file cùng thư mục, đúng tên và định dạng | ZIP chứa trực tiếp `video_1.txt` đến `video_5.txt`; mười cột, frame/ID nguyên hợp lệ, hộp có kích thước dương, không NaN/Inf, không trùng ID trong frame, ba cột cuối đều -1 | Đạt |
| Chỉ chấm số video_1 bằng nhãn gốc | Không có nhãn video_2–video_5; `gt.txt` và `seqinfo.ini` khớp nguyên ZIP tải; chấm lại file video_1 lấy trực tiếp từ ZIP bằng đúng commit TrackEval | Đạt |
| Báo cáo có cấu hình, lý do, quan sát và phương án loại cho từng video | Đủ năm dòng; có đối chiếu frame thử và giữa/cuối bản đầy đủ, có mục thử tiếp | Đạt |
| Ít nhất hai video có phân tích 3–5 câu | Có năm đoạn phân tích, mỗi đoạn bốn câu, gắn ngữ cảnh camera/mật độ/ánh sáng với lựa chọn và giới hạn | Đạt |
| Không commit ảnh lab, video preview hoặc trọng số | Kiểm tra danh sách file được Git theo dõi; không có các mục này | Đạt |

## Kiểm tra bản đầy đủ

| Video | Ảnh gốc | Frame log | Frame preview (ffprobe) | Dòng MOT trong ZIP |
|---|---:|---:|---:|---:|
| video_1 | 600 | 600 | 600 | 4.582 |
| video_2 | 1.050 | 1.050 | 1.050 | 13.821 |
| video_3 | 837 | 837 | 837 | 5.043 |
| video_4 | 900 | 900 | 900 | 6.220 |
| video_5 | 750 | 750 | 750 | 2.028 |

Tổng 4.137 frame. Tên ảnh tăng liên tục từ 1 đến số frame từng video.
Số dòng MOT không cần bằng số frame vì mỗi frame có thể có nhiều người
hoặc không có track. Đã đọc lại các frame lấy mẫu từ MP4 có vẽ ID thật,
bên cạnh các ảnh đối chiếu dựng từ kết quả MOT.

## Chấm lại độc lập từ ZIP

Lấy `video_1.txt` trực tiếp từ gói nộp, dùng nhãn gốc của giảng viên,
TrackEval commit `12c8791b303e0a0b50f753af204249e622d0281a` như bản Kaggle.
Chạy trên CPU cục bộ với HOTA/CLEAR/Identity; tắt vẽ biểu đồ vì môi trường
kiểm tra không có matplotlib, không đổi tham số metric hoặc tiền xử lý.

| Nguồn kết quả | HOTA | MOTA | IDF1 |
|---|---:|---:|---:|
| Kaggle bản cuối | 29,460 | 19,811 | 29,354 |
| Chấm lại từ ZIP | 29,460 | 19,811 | 29,354 |

Ba giá trị khớp nhau và khớp báo cáo. Log chấm lại tại
`runs/final_audit_20261009/metrics_recomputed.log`;
summary tại `runs/final_audit_20261009/TrackEval/data/trackers/mot_challenge/LAB-train/audit_zip_final/pedestrian_summary.txt`.

## Tính toàn vẹn và xác minh từ xa

- ZIP CRC hợp lệ; năm file kết quả khớp từng byte với đầu ra bản cuối.
- `BAO_CAO.md` trong ZIP khớp từng byte với báo cáo trong repo.
- SHA-256 ZIP khớp `submission/SHA256SUMS`:
  `ac873e8ab1753299911930f9436a1a6a7edd4fa38c8bfb68fcb88ff7a3cba289`.
- Chạy lại 31 unit test: tất cả đạt.
- Kiểm tra trực tiếp Kaggle: notebook chính vẫn COMPLETE.
- GitHub `main` khớp commit bản bài nộp `e19e9dd` tại thời điểm bắt đầu audit.

## Khác biệt đã giải thích và giới hạn

- Làm cá nhân theo yêu cầu của sinh viên, đã ghi đúng tên và MSSV.
- Chạy Kaggle theo yêu cầu thay cho môi trường conda cục bộ; giữ BoxMOT
  10.0.42, detector, Re-ID và các tham số bị khóa; ghi phiên bản thực tế.
- Gói tải không có `preview/` và `eval_config.json`. Dùng preview tracking
  đã xuất; chấm với tên thư mục chung LAB/train, giữ nguyên nhãn và seqinfo.
- HOTA/MOTA/IDF1 còn thấp; có bỏ sót và đổi ID, đặc biệt ở người nhỏ,
  nhóm che nhau và camera di chuyển. Báo cáo ghi rõ các lỗi quan sát được.
  Đề không đặt ngưỡng metric tối thiểu; giảng viên vẫn chấm chất lượng track.
- Bốn video khó chỉ có đánh giá trực quan trên frame lấy mẫu; không có
  số metric hoặc tuyên bố đã xác minh mọi ID xuyên suốt toàn bộ video.

Gói nộp giữ nguyên sau audit:
`submission/Day22_DoanQuangThang_2A202602395.zip`.
