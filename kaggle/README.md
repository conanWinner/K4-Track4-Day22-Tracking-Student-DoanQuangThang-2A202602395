# Chạy bài lab trên Kaggle bằng CLI

Dataset và notebook dùng chế độ riêng tư. Không đưa dữ liệu hoặc trọng số vào Git.

## 1. Chuẩn bị dữ liệu

Lấy đúng gói `data_lab21.zip` từ liên kết trong README. Script dưới kiểm tra
ảnh năm video, nhãn video_1, CRC của ZIP và đường dẫn giải nén.
Gói giảng viên thiếu eval_config.json: script dùng benchmark chung LAB,
split train, giữ nguyên nhãn và seqinfo.ini.
Thư mục upload phải là thư mục mới; ZIP gốc được giữ nguyên.

```bash
python scripts/prepare_kaggle_dataset.py \
  --archive /duong/dan/data_lab21.zip --owner thngonquang \
  --out lab_data/kaggle_upload_parts --part-size-mb 16
/home/conanwinner/.local/share/uv/tools/kaggle/bin/python \
  scripts/kaggle_parallel_cli.py datasets create -p lab_data/kaggle_upload_parts
```

Gói lớn được chia thành các phần 16 MiB để đường truyền có thể tiếp tục từng
tệp. Wrapper gọi Kaggle CLI với bốn kết nối upload và giữ thông tin tiếp tục
khi lỗi. Notebook ghép lại, kiểm tra SHA-256 từng phần và toàn bộ ZIP trước
khi giải nén. Dataset hiện tại đã sẵn sàng tại
https://www.kaggle.com/datasets/thngonquang/track4-day22-tracking-lab-data;
không chạy lại lệnh tạo dataset nếu chỉ muốn dùng bản đã upload.

## 2. Kiểm tra GPU và thư viện

```bash
python scripts/build_kaggle_notebook.py --owner thngonquang --preflight
kaggle kernels push -p kaggle/preflight
kaggle kernels status thngonquang/track4-day22-tracking-preflight
```

Đây chỉ là kiểm tra detector và năm tracker bằng ảnh tổng hợp, không phải kết
quả bài lab. Bản chạy phải có trạng thái COMPLETE và `preflight.json` passed.
BoxMOT 10.0.42 giữ nguyên; cài riêng không kéo NumPy 1.23.1 vì Kaggle sử dụng
Python mới. Notebook ghi phiên bản thư viện thực tế vào `versions.txt`.

## 3. Chạy thử trên dữ liệu thật

```bash
python scripts/build_kaggle_notebook.py --owner thngonquang \
  --dataset thngonquang/track4-day22-tracking-lab-data
kaggle kernels push -p kaggle/lab
kaggle kernels status thngonquang/track4-day22-tracking
kaggle kernels output thngonquang/track4-day22-tracking -p runs/kaggle_trials_v1
```

Mỗi video thử ByteTrack và BoT-SORT. Mỗi tracker có baseline conf=0.3,
iou=0.5; thử conf=0.15/0.5 và iou=0.4/0.7, mỗi lần đổi một tham số.
Hai baseline của video_1 chạy đủ 600 frame để so sánh HOTA/MOTA/IDF1.
Các lượt thử còn lại giới hạn 150 frame; video và log lưu riêng từng cấu hình.
Xem video có vẽ ID trước khi chọn cấu hình; không suy ra chất lượng chỉ từ số hộp.

## 4. Chạy đủ frame

Tạo `kaggle/selections.json` sau khi xem video, gồm khóa video_1 đến video_5.
Mỗi khóa chứa tracker, conf và iou. Không điền cấu hình trước khi có bằng chứng.

```bash
python scripts/build_kaggle_notebook.py --owner thngonquang \
  --dataset thngonquang/track4-day22-tracking-lab-data \
  --selections kaggle/selections.json
kaggle kernels push -p kaggle/lab
kaggle kernels status thngonquang/track4-day22-tracking
kaggle kernels output thngonquang/track4-day22-tracking -p runs/kaggle_final_v2
```

Bản cuối không giới hạn frame. Pipeline kiểm tra mười cột MOT, ID trùng,
giá trị bất thường và số ảnh xử lý qua log. Frame không có track không cần có
dòng MOT. TrackEval chấm duy nhất video_1; phiên bản TrackEval được ghi lại.

## 5. Hoàn thiện bài nộp

Điền báo cáo từ video thực tế và `metrics_video_1.log`. Nộp năm file txt và
báo cáo hoàn chỉnh. Không điền số metric cho video_2–video_5.
Không coi notebook RUNNING hoặc preflight passed là bài lab hoàn thành.

Sau khi điền báo cáo, đóng gói bằng script kiểm tra. Thư mục run-root là
thư mục day22 bên trong kết quả tải từ Kaggle. Script kiểm tra định dạng MOT,
log đủ frame và đếm frame video bằng ffprobe trước khi tạo ZIP mới.

```bash
python scripts/package_submission.py \
  --run-root runs/kaggle_final_v2/day22 \
  --report submission_template/BAO_CAO_mau.md \
  --output submission/Day22_DoanQuangThang_2A202602395.zip
```
