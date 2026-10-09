"""Chạy thử hoặc chạy bản nộp trên Kaggle từ đúng gói dữ liệu lab."""

import json
import configparser
import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from submission_checks import parse_metric_summary, validate_mot_rows, validate_zip_members
from archive_parts import assemble_archive


def evaluate(trackeval: Path, lab: Path, submission: Path, run_name: str, output: Path) -> dict:
    """Chấm một file video_1 và xác minh có summary hợp lệ.

    Args:
        trackeval: Thư mục cài TrackEval.
        lab: Gốc dữ liệu lab.
        submission: File video_1.txt đã chạy đủ frame.
        run_name: Tên riêng cho lượt chấm.
        output: Thư mục lưu log và summary.

    Returns:
        Dict metric HOTA, MOTA và IDF1 theo phần trăm.

    Raises:
        RuntimeError: Khi TrackEval không tạo summary duy nhất.
    """
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'metrics_video_1.log').open('w') as log:
        subprocess.run([sys.executable, 'scripts/evaluate_practice.py', '--trackeval-root', str(trackeval),
            '--lab-data-root', str(lab), '--submission', str(submission), '--run-name', run_name],
            stdout=log, stderr=subprocess.STDOUT, check=True)
    summaries = list((trackeval / 'data/trackers/mot_challenge').glob(f'*/{run_name}/pedestrian_summary.txt'))
    if len(summaries) != 1:
        raise RuntimeError('TrackEval không tạo được summary duy nhất.')
    content = summaries[0].read_text()
    metrics = parse_metric_summary(content)
    (output / 'metrics_video_1_summary.txt').write_text(content)
    (output / 'metrics_video_1.json').write_text(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    """Thử cấu hình, ghi log và kiểm tra bản nộp đủ frame trước khi đóng gói."""
    work = Path.cwd()
    candidates = [path for path in Path('/kaggle/input').rglob('video_1/img1')
                  if '__MACOSX' not in path.parts]
    if not candidates:
        archives = list(Path('/kaggle/input').rglob('data_lab21.zip'))
        if not archives:
            manifests = list(Path('/kaggle/input').rglob('data_parts.json'))
            if len(manifests) == 1:
                joined = Path('/tmp/day22_data_lab21.zip')
                assemble_archive(manifests[0], joined)
                archives = [joined]
                print('Đã ghép dữ liệu, SHA-256 khớp ZIP gốc.', flush=True)
        if len(archives) != 1:
            raise RuntimeError('Cần gắn đúng một gói data_lab21.zip hoặc cây ảnh lab.')
        destination = Path('/tmp/day22_lab_data_extracted')
        destination.mkdir(exist_ok=False)
        with zipfile.ZipFile(archives[0]) as archive:
            validate_zip_members(archive.namelist())
            archive.extractall(destination)
        candidates = [path for path in destination.rglob('video_1/img1')
                      if '__MACOSX' not in path.parts]
    if len(candidates) != 1:
        raise RuntimeError('Không xác định được duy nhất thư mục ảnh của lab.')
    lab = candidates[0].parent.parent
    os.environ['LAB_DATA'] = str(lab)
    videos = [f'video_{i}' for i in range(1, 6)]
    counts = {}
    for video in videos:
        frames = sorted((lab / video / 'img1').glob('*.jpg'))
        if not frames:
            raise RuntimeError(f'{video}: thiếu ảnh')
        if video != 'video_1' and (lab / video / 'gt' / 'gt.txt').exists():
            raise RuntimeError('Gói học viên không được có nhãn video_2–video_5.')
        counts[video] = len(frames)
    for name in ['gt/gt.txt', 'seqinfo.ini']:
        if not (lab / 'video_1' / name).is_file():
            raise RuntimeError(f'Thiếu video_1/{name}')
    (work / 'data_inventory.json').write_text(json.dumps(counts, indent=2))
    subprocess.run([sys.executable, 'scripts/check_data.py', '--lab-data-root', str(lab)], check=True)
    subprocess.run([sys.executable, '-m', 'nbconvert', '--to', 'notebook', '--execute',
        '--ExecutePreprocessor.timeout=300', '--output', 'on_tap_metrics_da_chay.ipynb',
        'on_tap_metrics.ipynb'], check=True)
    mode = os.environ.get('LAB_MODE', 'trials')
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('Bài chạy Kaggle chưa có GPU.')
    (work / 'runtime_info.json').write_text(json.dumps({
        'python': sys.version, 'gpu': torch.cuda.get_device_name(0), 'mode': mode}, indent=2))
    sequence = configparser.ConfigParser()
    sequence.read(lab / 'video_1/seqinfo.ini')
    fps_video1 = sequence.getint('Sequence', 'frameRate')
    trackeval = Path('/tmp/day22_TrackEval')
    subprocess.run(['git', 'clone', 'https://github.com/JonathonLuiten/TrackEval.git', str(trackeval)], check=True)
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps', '-e', str(trackeval)], check=True)
    with (work / 'trackeval_commit.txt').open('w') as record:
        subprocess.run(['git', '-C', str(trackeval), 'rev-parse', 'HEAD'], stdout=record, check=True)
    results = []
    if mode == 'trials':
        configs = [
            ('bytetrack', .3, .5), ('botsort', .3, .5),
            ('botsort', .15, .5), ('botsort', .5, .5),
            ('botsort', .3, .4), ('botsort', .3, .7),
            ('bytetrack', .15, .5), ('bytetrack', .5, .5),
            ('bytetrack', .3, .4), ('bytetrack', .3, .7),
        ]
        for video in videos:
            for tracker, conf, iou in configs:
                label = f'{tracker}_conf{conf}_iou{iou}'
                out = work / 'runs' / 'thu_nghiem' / label
                out.mkdir(parents=True, exist_ok=True)
                limit = counts[video] if video == 'video_1' and conf == .3 and iou == .5 else min(150, counts[video])
                command = [sys.executable, 'scripts/run_tracking.py', '--source', str(lab / video / 'img1'),
                    '--seq-name', video, '--tracker', tracker, '--conf', str(conf), '--iou', str(iou),
                    '--out', str(out), '--save-video', '--device', 'cuda:0', '--max-frames', str(limit),
                    '--fps', str(fps_video1 if video == 'video_1' else 20)]
                print(f'Đang thử {video}: {label}', flush=True)
                with (out / f'{video}.log').open('w') as log:
                    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
                validate_mot_rows((out / f'{video}.txt').read_text(), limit)
                metrics = None
                if video == 'video_1' and limit == counts[video]:
                    metrics = evaluate(trackeval, lab, out / 'video_1.txt', label, out)
                results.append({'video': video, 'tracker': tracker, 'conf': conf, 'iou': iou,
                    'processed_frames': limit, 'output': str(out.relative_to(work)), 'metrics': metrics})
                (work / 'experiments.json').write_text(json.dumps(results, indent=2))
        (work / 'experiments.json').write_text(json.dumps(results, indent=2))
        print('Đã chạy thử. Cần xem video, chọn cấu hình rồi chạy chế độ final.')
    elif mode == 'final':
        selections = json.loads((work / 'selections.json').read_text())
        if set(selections) != set(videos):
            raise RuntimeError('Cấu hình cuối phải chứa đủ năm video.')
        out = work / 'runs' / 'nop_bai'
        out.mkdir(parents=True, exist_ok=True)
        for video in videos:
            cfg = selections[video]
            command = [sys.executable, 'scripts/run_tracking.py', '--source', str(lab / video / 'img1'),
                '--seq-name', video, '--tracker', cfg['tracker'], '--conf', str(cfg['conf']), '--iou', str(cfg['iou']),
                '--out', str(out), '--save-video', '--device', 'cuda:0',
                '--fps', str(fps_video1 if video == 'video_1' else 20)]
            print(f'Đang chạy đủ frame {video}: {cfg}', flush=True)
            with (out / f'{video}.log').open('w') as log:
                subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
            validate_mot_rows((out / f'{video}.txt').read_text(), counts[video])
            log_text = (out / f'{video}.log').read_text()
            if f'-> {counts[video]} frame ' not in log_text:
                raise RuntimeError(f'{video}: chưa chứng minh đã xử lý đủ ảnh.')
        evaluate(trackeval, lab, out / 'video_1.txt', 'day22_final', work)
        print('Đã chạy đủ frame và chấm video_1. Cần hoàn thiện báo cáo từ video thực tế.')
    else:
        raise RuntimeError('LAB_MODE phải là trials hoặc final.')
    weight_hashes = {}
    for name in ['yolo26n.pt', 'osnet_x0_25_msmt17.pt']:
        with (work / name).open('rb') as weight:
            weight_hashes[name] = hashlib.file_digest(weight, 'sha256').hexdigest()
    (work / 'weights_sha256.json').write_text(json.dumps(weight_hashes, indent=2))


if __name__ == '__main__':
    main()
