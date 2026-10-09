# Lab Tracking — 2 giờ

Nhóm 2 người một máy. Detector đã khóa. Bạn chọn tracker và ngưỡng cho năm video khác cảnh.

## Bài làm cá nhân đã hoàn thành

Đoàn Quang Thắng — MSSV 2A202602395. Đã chạy 50 lượt thử và bản cuối
đủ 4.137 frame trên Kaggle Tesla T4; cả hai notebook đều COMPLETE.
31 kiểm thử đạt ở máy cục bộ và Kaggle. Năm preview được đếm frame bằng
ffprobe và khớp 600 / 1.050 / 837 / 900 / 750 ảnh gốc.

- [Gói nộp: năm file MOT, báo cáo và bằng chứng](submission/Day22_DoanQuangThang_2A202602395.zip).
- [Báo cáo hoàn chỉnh](submission_template/BAO_CAO_mau.md),
  [thử nghiệm và lý do chọn cấu hình](kaggle/THU_NGHIEM.md).
- [Đối chiếu yêu cầu lần cuối và chấm lại độc lập từ ZIP](kaggle/KIEM_TRA_CUOI.md).
- [Notebook Kaggle](https://www.kaggle.com/code/thngonquang/track4-day22-tracking)
  (riêng tư, phiên bản 2 là bản đầy đủ).

Video_1: HOTA **29,460**, MOTA **19,811**, IDF1 **29,354** theo thang
phần trăm. Báo cáo ghi rõ các lỗi bỏ sót và đổi ID còn tồn tại;
video_2–video_5 chỉ đánh giá bằng mắt.

## Việc cần làm

1. Tạo môi trường một lần:

```bash
conda env create -f environment.yml
conda activate cv_robotics_lab21
git clone https://github.com/JonathonLuiten/TrackEval.git
pip install -e TrackEval/
```

2. Tải ảnh năm video: [data_lab21.zip](https://drive.google.com/file/d/1UeVPQd6j5pSzxoJDcKJrerT9SL3vJLDt/view?usp=sharing). Giải nén, rồi gán đường dẫn thư mục chứa `video_1` … `video_5`:

```bash
export LAB_DATA=/đường/dẫn/lab_data
python scripts/check_data.py --lab-data-root "$LAB_DATA"
```

Cả năm video phải có ảnh. Chỉ `video_1` có nhãn.

3. Mở `on_tap_metrics.ipynb` bằng kernel env này. Đọc bảng MOTA / IDF1 / HOTA, rồi chạy YOLO trên một ảnh `video_1`.

4. Chạy tracker. Bản thử có thể giới hạn frame. Bản nộp thì không.

```bash
python scripts/run_tracking.py \
  --source "$LAB_DATA/video_1/img1" \
  --seq-name video_1 \
  --tracker bytetrack --conf 0.3 --iou 0.5 \
  --out runs/nop_bai --save-video
```

Đổi `--seq-name` và thư mục `img1` cho `video_2` … `video_5`. Tracker được chọn: `bytetrack`, `ocsort`, `botsort`, `strongsort`, `deepocsort`.

5. Chấm số **chỉ** `video_1`:

```bash
python scripts/evaluate_practice.py \
  --trackeval-root ~/TrackEval \
  --lab-data-root "$LAB_DATA" \
  --submission runs/nop_bai/video_1.txt \
  --run-name nhom01_video1
```

`video_2` đến `video_5` không có nhãn. Xem `preview/video_N.mp4` và video có vẽ ID, rồi ghi điều bạn thấy.

## Luật chơi

| Khóa | Bạn chọn |
|---|---|
| Detector `yolo26n.pt`, ảnh 640 px, lớp người, Re-ID `osnet_x0_25_msmt17.pt` | Tracker, `--conf`, `--iou` của detector |

## Nộp

- `video_1.txt` … `video_5.txt` trong `runs/nop_bai/` (đủ frame, đúng tên).
- `submission_template/BAO_CAO_mau.md` đã điền. Số HOTA / MOTA / IDF1 chỉ bắt buộc cho `video_1`.

Chi tiết từng bước, sự cố, và lịch 2 giờ: [HUONG_DAN.md](HUONG_DAN.md).

Chạy trên GPU Kaggle bằng CLI: [kaggle/README.md](kaggle/README.md).
Dataset và notebook của bài làm cá nhân dùng chế độ riêng tư;
tiến độ có bằng chứng được ghi trong [kaggle/TIEN_DO.md](kaggle/TIEN_DO.md).
