# Báo cáo lab: chọn tracker cho 5 video

**Hình thức:** Làm cá nhân. **Sinh viên:** Đoàn Quang Thắng — **MSSV:** 2A202602395.

Detector giữ nguyên `yolo26n.pt`, kích thước đầu vào 640 px, lớp người (0).
Các tracker có ngoại hình dùng `osnet_x0_25_msmt17.pt`. Chỉ đổi tracker và
ngưỡng `conf` / `iou` của detector; giữ cấu hình nội bộ tracker theo đề.

## 1. Cách thử và cấu hình đã chọn

Mỗi video thử ByteTrack (chuyển động) và BoT-SORT (chuyển động + Re-ID,
tức nhận dạng lại bằng ngoại hình). Với mỗi tracker, chạy năm cặp ngưỡng:
`(0,30; 0,50)`, `(0,15; 0,50)`, `(0,50; 0,50)`, `(0,30; 0,40)` và
`(0,30; 0,70)`; mỗi lần chỉ đổi một tham số so với mốc 0,30/0,50.
Tổng cộng 50 lượt, 8.400 frame xử lý; hai mốc video_1 chạy 600 frame để
chấm số, các lượt khác chạy 150 frame. Đối chiếu hộp và ID trên cùng
frame 30/80/150; so ngưỡng ở frame 80/150. Nhận xét trực quan dựa trên
frame lấy mẫu, không phải thống kê lỗi có nhãn cho bốn video khó.

| Video | Tracker | conf | iou | Quan sát dùng để chọn | Đã thử nhưng loại |
|---|---|---:|---:|---|---|
| video_1 — quảng trường, tĩnh, ban ngày | BoT-SORT | 0,30 | 0,50 | Hai người phía trước có hộp ổn định; điểm HOTA/MOTA/IDF1 cao hơn ByteTrack trên toàn bộ 600 frame. Vẫn thấy người áo tím đổi ID 3 → 37 giữa frame 80 và 150. | ByteTrack 0,30/0,50 có điểm tổng hợp thấp hơn; BoT-SORT conf=0,50 mất người nhỏ gần cửa phải ở frame 80; iou=0,70 có hộp chồng trên áo tím ở frame 80. |
| video_2 — phố đêm, tĩnh, đông | BoT-SORT | 0,15 | 0,50 | Người trái và người gần xe giữ ID 1/2/5 ở các frame lấy mẫu. Ngưỡng thấp giữ thêm người nhỏ sát cột đèn phía dưới ở frame 150, ID 24. | BoT-SORT conf=0,50 bỏ người ở vùng giữa/phía xa tại frame 150; ByteTrack baseline thiếu track người sát biển cửa hàng trái ở frame 30. |
| video_3 — camera di chuyển, ảnh nhỏ | BoT-SORT | 0,15 | 0,50 | Áo sọc giữ ID 1, áo xanh trái giữ ID 2; người áo tối giữa hai người giữ ID 17 ở frame 80/150. Có thêm hộp người nhỏ phía xa tại frame 150, ID 40. | BoT-SORT conf=0,50 vẫn giữ người gần nhưng thiếu người nhỏ này; ByteTrack baseline chưa cho lợi ích rõ với người bị che ở giữa. |
| video_4 — trong nhà, camera tiến tới | BoT-SORT | 0,30 | 0,50 | Áo đỏ giữ ID 2, áo sáng đi trước giữ ID 6 tại frame 30/80/150; vẫn có track người nhỏ bên trái ở frame 80. | ByteTrack giữ người chính nhưng ít track người nhỏ hơn ở frame 80; BoT-SORT iou=0,70 có hộp gần chồng trong nhóm trước áo đỏ ở frame 150. |
| video_5 — camera trên xe bus | ByteTrack | 0,30 | 0,50 | Áo đỏ vỉa hè phải giữ ID 2 tại frame 30/80; hai người phía trái giữ ID 12/13. Chưa thấy lợi ích giữ ID rõ của BoT-SORT trong đoạn mẫu. | ByteTrack conf=0,50 đổi ID người trái từ 12 ở frame 30 sang 18 ở frame 80 trong cùng lượt chạy; BoT-SORT 0,30/0,50 tốn thời gian hơn. |

## 2. Số liệu video_1

Bảng so sánh hai lượt thử đủ 600 frame, cùng conf=0,30 và iou=0,50:

| Tracker | HOTA | MOTA | IDF1 | Bỏ sót (FN) | Hộp giả (FP) | Đổi ID |
|---|---:|---:|---:|---:|---:|---:|
| ByteTrack | 26,912 | 17,292 | 25,713 | 15.249 | 107 | 12 |
| BoT-SORT | 29,460 | 19,811 | 29,354 | 14.538 | 337 | 25 |

Bản nộp chạy lại đủ 600 frame bằng BoT-SORT. Ba cột trích từ
`metrics_video_1_summary.txt` của lượt `day22_final`, theo thang phần trăm:

```text
HOTA    MOTA    IDF1
29.460  19.811  29.354
```

Log đầy đủ kèm bài nộp trong `metrics_video_1.log`. Chỉ video_1 được chấm;
video_2–video_5 không có nhãn và không được gán số HOTA/MOTA/IDF1.
Gói giảng viên thiếu `eval_config.json`, nên dùng tên thư mục chấm chung
`LAB/train` với TrackEval, giữ nguyên `gt.txt` và `seqinfo.ini`.

## 3. Phân tích

**video_1:** Camera đứng yên và người gần có ngoại hình rõ, phù hợp để
kết hợp chuyển động với Re-ID. BoT-SORT tăng HOTA 2,548 điểm phần trăm
và IDF1 3,641 điểm phần trăm so với ByteTrack, nên được chọn theo điểm
tổng hợp. Tuy nhiên BoT-SORT có 25 lần đổi ID và 337 hộp giả, cao hơn
12 và 107 của ByteTrack; người áo tím trong đoạn mẫu cũng bị đổi ID.
Số bỏ sót 14.538 còn lớn, phù hợp với việc nhiều người nhỏ/phía xa không
có hộp, nên kết quả chưa thể xem là tracking tốt cho toàn cảnh.

**video_2:** Cảnh đêm đông người, ánh đèn mạnh và các nhóm che nhau làm
người nhỏ khó phát hiện ổn định. Với conf=0,15, hộp người nhỏ sát cột đèn
ở frame 150 còn xuất hiện, trong khi conf=0,50 bỏ thêm người phía xa.
BoT-SORT giữ ID của vài người gần qua các frame mẫu và xuất track người
sát biển cửa hàng mà ByteTrack baseline thiếu ở frame 30. Vì chưa có
nhãn, lựa chọn này ưu tiên giảm bỏ sót nhìn thấy; chưa chứng minh được
nó ít đổi ID hoặc ít hộp giả hơn trên toàn bộ cảnh.

**video_3:** Camera di chuyển làm vị trí hộp đổi mạnh và người áo tối
bị hai người gần che một phần, nên sử dụng thêm ngoại hình là lựa chọn
hợp lý để hỗ trợ ghép track. Trong các frame mẫu, BoT-SORT giữ ID 1/2
của hai người gần và ID 17 của người ở giữa từ frame 80 đến 150.
Conf=0,15 giữ thêm người nhỏ phía xa tại frame 150 so với hai ngưỡng cao
hơn. Đây là lợi ích quan sát được về độ bao phủ, chưa đủ để khẳng định
Re-ID đã giải quyết mọi trường hợp che khuất hoặc rung camera.

**video_4:** Camera tiến tới trong nhà làm kích thước người thay đổi,
đồng thời nền kính và sàn phản chiếu gây khó cho việc xem hộp. BoT-SORT
giữ ID 2 của áo đỏ và ID 6 của áo sáng ở frame 30/80/150, nhưng ByteTrack
cũng giữ được hai người chính. Chọn BoT-SORT vì có thêm track người nhỏ
bên trái ở frame 80, giữ conf=0,30 vì hạ xuống 0,15 chưa cải thiện rõ các
người chính. IoU=0,70 có hộp gần chồng ở nhóm trước áo đỏ tại frame 150,
nên giữ 0,50 và vẫn cần kiểm tra lỗi ở phần đông hơn của video.

**video_5:** Camera trên xe thay đổi góc nhìn nhanh, còn người ở hai
vỉa hè thường nhỏ và dễ ra khỏi khung. ByteTrack baseline giữ ID 2 ở
bên phải và 12/13 ở bên trái từ frame 30 đến 80; conf=0,50 làm một
người trái đổi từ ID 12 sang 18 trong chính lượt chạy đó. Trong lượt
150 frame, ByteTrack baseline mất 8,0 giây so với BoT-SORT 21,3 giây,
trong khi chưa thấy lợi ích giữ ID rõ của tracker có Re-ID trên các
frame mẫu. Chọn ByteTrack 0,30/0,50 theo đánh đổi quan sát và thời gian;
người ra khỏi khung không được coi là lỗi chỉ vì ID biến mất.

## 4. Nếu có thêm thời gian

Quét conf mịn hơn trong khoảng 0,15–0,30 và chấm đầy đủ video_1, đồng
thời xem các đoạn người cắt nhau để tìm frame đổi ID. Tiếp tục kiểm tra
người xa và phản chiếu ở bốn video khó, giữ nguyên detector và Re-ID
của bài chính.

## 5. Bằng chứng chạy và bài nộp

Notebook thử phiên bản 1 và bản đầy đủ phiên bản 2 đều COMPLETE trên
Kaggle. Bản đầy đủ bỏ giới hạn `--max-frames`; số ảnh lần lượt là
600 / 1.050 / 837 / 900 / 750, tổng 4.137 frame.
Notebook ôn tập đã thực thi trên dữ liệu thật, đúng cả ba câu True/False.

Đã kiểm tra thêm đầu ra bản đầy đủ ở các frame giữa/cuối, bên cạnh
các frame dùng chọn cấu hình. Các vấn đề dưới đây còn tồn tại:

| Video | Frame kiểm tra thêm | Quan sát bản đầy đủ |
|---|---|---|
| video_1 | 200/400/600 | Người áo tím giữ ID 37 ở frame 200/400 sau lần đổi ID trong đoạn thử; người phía xa còn nhiều trường hợp không có hộp. |
| video_2 | 350/700/1050 | Người đứng sát cửa hàng phải giữ ID 4 ở cả ba frame; nhóm đông góc trên trái vẫn bị bỏ sót nhiều. |
| video_3 | 280/560/837 | Có hộp trên người gần và một phần nhóm đi ngược chiều; khi camera tiến vào nhóm đông, các hộp che nhau và xuất hiện nhiều track mới. Chưa chứng minh giữ danh tính xuyên suốt. |
| video_4 | 300/600/900 | Người áo sáng đi trước có ID 6 ở frame 300 nhưng ID 49 ở frame 600, cho thấy lựa chọn vẫn có lỗi đổi ID ngoài đoạn thử. |
| video_5 | 250/500/750 | Frame 250 còn track trên người bên phải; tại frame 500 hai người đứng rõ gần cửa hàng không có track. Đây là bỏ sót còn tồn tại, cần ưu tiên kiểm tra lại nếu tiếp tục tối ưu. |

Môi trường bản cuối: GPU Tesla T4, Python 3.13.15, BoxMOT 10.0.42;
phiên bản đầy đủ được lưu trong `versions.txt`.

- Notebook: https://www.kaggle.com/code/thngonquang/track4-day22-tracking
- Cấu hình: `selections.json`; số ảnh: `data_inventory.json`.
- Môi trường và trọng số: `versions.txt`, `runtime_info.json`,
  `weights_sha256.json`, `trackeval_commit.txt`.
- Kết quả: `video_1.txt` … `video_5.txt`, định dạng MOT mười cột.
- `KIEM_TRA.json` ghi số dòng MOT, số frame xử lý và số frame preview
  được đếm bằng ffprobe; frame không có track không bắt buộc có dòng MOT.

Video preview dùng 30 FPS cho video_1 theo seqinfo; bốn video khác dùng
20 FPS để xem vì gói không có thông tin FPS của chúng. Tốc độ preview
không được dùng để suy ra thời gian thực hay điểm chất lượng tracking.
