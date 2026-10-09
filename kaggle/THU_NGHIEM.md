# Bằng chứng chọn cấu hình

Lượt thử Kaggle phiên bản 1 đã COMPLETE. Manifest `experiments.json` chứa
50 lượt và 8.400 frame xử lý. Cả 50 file MOT qua kiểm tra mười cột,
giá trị hữu hạn, ID không trùng trong cùng frame và log đúng số frame.
Notebook ôn tập thực thi trên ảnh thật: ba đáp án đúng; frame đầu có
6 hộp người với conf=0,3, 14 hộp với conf=0,15 và 5 hộp với conf=0,5.

## Các lượt đã chạy

Mỗi video thử ByteTrack và BoT-SORT; mỗi tracker có năm cấu hình:

| conf | iou | Mục đích |
|---:|---:|---|
| 0,30 | 0,50 | Mốc so sánh |
| 0,15 | 0,50 | Hạ riêng ngưỡng phát hiện |
| 0,50 | 0,50 | Tăng riêng ngưỡng phát hiện |
| 0,30 | 0,40 | Hạ riêng ngưỡng IoU |
| 0,30 | 0,70 | Tăng riêng ngưỡng IoU |

Hai mốc so sánh video_1 chạy 600 frame. Tất cả lượt khác chạy 150 frame.
Chỉ hai lượt đủ 600 frame được chấm số; không so điểm đoạn 150 frame
với nhãn toàn bộ 600 frame.

## Số liệu thực tế video_1

| Tracker (conf=0,30, iou=0,50) | HOTA | MOTA | IDF1 | Bỏ sót (FN) | Hộp giả (FP) | Đổi ID |
|---|---:|---:|---:|---:|---:|---:|
| ByteTrack | 26,912 | 17,292 | 25,713 | 15.249 | 107 | 12 |
| BoT-SORT | 29,460 | 19,811 | 29,354 | 14.538 | 337 | 25 |

Metric theo thang phần trăm do TrackEval xuất. BoT-SORT tăng HOTA
2,548 điểm phần trăm và IDF1 3,641 điểm phần trăm nhưng có nhiều hộp giả
và lần đổi ID hơn. Lý do chọn là kết quả tổng hợp cao hơn, không phải
khẳng định BoT-SORT giữ mọi người tốt hơn ByteTrack.

## Quan sát chọn cấu hình

Đối chiếu ảnh có hộp và ID ở cùng frame 30/80/150 giữa hai tracker;
so ngưỡng ở frame 80/150. Đây là quan sát trên các frame lấy mẫu,
chưa khẳng định đã xem liên tục toàn bộ video.

- video_1: chọn BoT-SORT 0,30/0,50 theo hai lượt chấm đủ frame. Ngưỡng
  conf=0,50 mất hộp của người nhỏ gần cửa bên phải ở frame 80; iou=0,70
  tạo thêm hộp chồng trên người áo tím ở frame 80. BoT-SORT vẫn đổi
  ID người áo tím từ 3 ở frame 80 sang 37 ở frame 150.
- video_2: chọn BoT-SORT 0,15/0,50. Người đi bộ bên trái và người đứng
  gần xe giữ các ID 1/2/5 trong các frame lấy mẫu. Ở frame 150,
  conf=0,15 còn hộp trên người nhỏ sát cột đèn phía dưới (ID 24),
  trong khi conf=0,50 bỏ thêm người ở vùng giữa và bên phải phía xa.
  BoT-SORT baseline có hộp người sát biển cửa hàng bên trái tại frame 30
  mà ByteTrack baseline không xuất track. Đây không phải điểm định lượng.
- video_3: chọn BoT-SORT 0,15/0,50. Áo sọc giữ ID 1 và áo xanh bên trái
  giữ ID 2 ở frame 30/80/150; người áo tối giữa hai người giữ ID 17
  ở frame 80/150. Ngưỡng thấp còn có hộp cho người nhỏ phía xa giữa
  hai người ở frame 150 (ID 40), thiếu ở conf=0,30/0,50. Không suy ra
  ID 17 của BoT-SORT tốt hơn ID 24 của ByteTrack chỉ vì số ID khác nhau.
- video_4: chọn BoT-SORT 0,30/0,50. Người áo đỏ giữ ID 2, người áo
  sáng trước camera giữ ID 6 ở frame 30/80/150. Hai tracker cùng giữ
  được các đối tượng chính; BoT-SORT có thêm track người nhỏ bên trái
  tại frame 80. Hạ conf=0,15 chưa cho lợi ích rõ với người chính;
  iou=0,70 có hộp gần chồng ở nhóm người trước áo đỏ tại frame 150.
- video_5: chọn ByteTrack 0,30/0,50. Người áo đỏ trên vỉa hè phải giữ
  ID 2 ở frame 30/80; hai người phía trái giữ ID 12/13. Ba mức iou
  không cho khác biệt trực quan rõ ở frame 80/150. BoT-SORT có thêm
  track người xa nhưng chưa thấy lợi ích giữ ID rõ; conf=0,50 của
  ByteTrack đổi ID người bên trái từ 12 ở frame 30 sang 18 ở frame 80
  trong chính lượt conf=0,50, còn baseline giữ ID 12. Các đối tượng
  ra khỏi khung ở frame 150 không được tính
  là lỗi chỉ từ việc ID không còn xuất hiện.

Ảnh đối chiếu: `runs/inspection/video_N_compare_baseline.jpg`,
`video_N_compare_conf.jpg` và `video_N_compare_iou.jpg`.
Đầu ra gốc: `runs/kaggle_trials_v1/day22/runs/thu_nghiem/`.

## Cấu hình cho lượt đầy đủ

`selections.json` chốt các lựa chọn trên. Phiên bản 2 của notebook chính
đã COMPLETE, chạy lại đủ năm video. Năm file MOT và log được xác minh;
ffprobe đếm đúng 600 / 1.050 / 837 / 900 / 750 frame preview.
Metric video_1 của bản cuối khớp bảng BoT-SORT phía trên.
Báo cáo có thêm quan sát giữa/cuối từng video, bao gồm các lỗi còn tồn tại.
Gói `submission/Day22_DoanQuangThang_2A202602395.zip` đã sẵn sàng nộp.
