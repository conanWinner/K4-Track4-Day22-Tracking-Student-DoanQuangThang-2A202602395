"""Kiểm tra bằng chứng full-frame rồi đóng gói năm kết quả và báo cáo."""

import argparse
import json
import subprocess
import zipfile
from pathlib import Path

from submission_checks import parse_metric_summary, validate_mot_rows


def main() -> None:
    """Tạo ZIP bài nộp mới, không ghi đè các gói hoặc kết quả hiện có."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-root', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.run_root
    counts = json.loads((root / 'data_inventory.json').read_text())
    choices = json.loads((root / 'selections.json').read_text())
    report = args.report.read_text()
    if any(marker in report for marker in ['……………………', '(dán output ở đây)', 'TODO']):
        raise ValueError('Báo cáo còn mục chưa điền.')
    metrics = parse_metric_summary((root / 'metrics_video_1_summary.txt').read_text())
    files = {}
    evidence = {'metrics_video_1': metrics, 'videos': {}}
    for index in range(1, 6):
        video = f'video_{index}'
        result = root / 'runs/nop_bai' / f'{video}.txt'
        rows = validate_mot_rows(result.read_text(), counts[video])
        log = (result.parent / f'{video}.log').read_text()
        if f'-> {counts[video]} frame ' not in log:
            raise ValueError(f'{video}: thiếu bằng chứng xử lý đủ frame.')
        preview = result.parent / f'{video}_preview.mp4'
        count = subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames',
            '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(preview)], text=True).strip()
        if int(count) != counts[video]:
            raise ValueError(f'{video}: số frame preview không khớp ảnh gốc.')
        files[f'{video}.txt'] = result
        evidence['videos'][video] = {'processed_frames': counts[video], 'mot_rows': rows,
            'preview_frames': int(count), 'configuration': choices[video]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, source in files.items():
            archive.write(source, name)
        archive.write(args.report, 'BAO_CAO.md')
        archive.writestr('KIEM_TRA.json', json.dumps(evidence, ensure_ascii=False, indent=2))
        archive.write(root / 'metrics_video_1.log', 'metrics_video_1.log')
        archive.write(root / 'versions.txt', 'versions.txt')
        for name in ['selections.json', 'data_inventory.json', 'runtime_info.json',
                     'weights_sha256.json', 'trackeval_commit.txt']:
            archive.write(root / name, name)
    print(json.dumps({'status': 'SẴN SÀNG NỘP', 'archive': str(args.output),
        'evidence': evidence}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
