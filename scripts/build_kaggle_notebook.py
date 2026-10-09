"""Đóng gói code hiện tại thành notebook chạy trong phiên Kaggle riêng."""

import argparse
import json
from pathlib import Path


def main() -> None:
    """Tạo notebook và metadata riêng tư, không upload hoặc chạy từ xa."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--dataset", default="")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--selections", type=Path, help="JSON cấu hình đã chọn sau khi xem video thử")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root / "kaggle" / ("preflight" if args.preflight else "lab")
    target.mkdir(parents=True, exist_ok=True)
    cells = []
    cells.append({"cell_type": "markdown", "metadata": {}, "source": [
        "# Lab Day22 — tracking trên năm video\n",
        "Detector và Re-ID giữ nguyên theo đề. Chỉ video_1 có số liệu chấm.\n",
        "Bản preflight chỉ kiểm tra môi trường, không tạo kết quả bài nộp."
    ]})
    sources = {}
    for pattern in ("scripts/*.py", "tests/*.py"):
        for path in sorted(root.glob(pattern)):
            sources[str(path.relative_to(root))] = path.read_text()
    sources["pytest.ini"] = (root / "pytest.ini").read_text()
    sources["on_tap_metrics.ipynb"] = (root / "on_tap_metrics.ipynb").read_text()
    sources["requirements-kaggle.txt"] = (root / "requirements-kaggle.txt").read_text()
    setup = '''import json, os, subprocess, sys, shutil
from pathlib import Path
WORK = Path('/kaggle/working/day22')
WORK.mkdir(parents=True, exist_ok=True)
os.chdir(WORK)
'''
    setup += "SOURCES = " + repr(sources) + "\n"
    setup += '''for name, content in SOURCES.items():
    destination = WORK / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content)
for weight in ['yolo26n.pt', 'osnet_x0_25_msmt17.pt']:
    cached = list(Path('/kaggle/input').rglob(weight))
    if len(cached) == 1 and not (WORK / weight).exists():
        shutil.copy2(cached[0], WORK / weight)
        print(f'Dùng lại trọng số đã kiểm thử: {weight}')
# Kaggle hiện chạy Python 3.13: giữ thư viện GPU có sẵn của phiên.
# BoxMOT cũ pin NumPy 1.23.1 không có wheel tương thích; cài riêng
# không kéo dependency, rồi kiểm tra đủ năm tracker với NumPy của Kaggle.
PYTHON = sys.executable
subprocess.run([PYTHON, '-m', 'pip', 'install', '-r', 'requirements-kaggle.txt'], check=True)
subprocess.run([PYTHON, '-m', 'pip', 'install', '--no-deps', 'boxmot==10.0.42'], check=True)
subprocess.run([PYTHON, '-m', 'pytest', '-q'], check=True)
subprocess.run([PYTHON, '-m', 'pip', 'freeze'], check=True, stdout=(WORK / 'versions.txt').open('w'))
'''
    cells.append({"cell_type": "code", "metadata": {}, "source": setup.splitlines(True), "outputs": [], "execution_count": None})
    if args.preflight:
        smoke = '''import textwrap
smoke_code = r"""
import json
from pathlib import Path
import cv2, numpy as np, torch
from ultralytics import YOLO
from boxmot.tracker_zoo import create_tracker, get_tracker_config
assert torch.cuda.is_available(), 'Chưa có GPU'
model = YOLO('yolo26n.pt').to('cuda:0')
model.predict(np.zeros((640, 640, 3), dtype=np.uint8), imgsz=640, classes=[0], device='cuda:0', verbose=False)
results = {}
for name in ['bytetrack', 'ocsort', 'botsort', 'strongsort', 'deepocsort']:
    tracker = create_tracker(name, get_tracker_config(name), Path('osnet_x0_25_msmt17.pt'), torch.device('cuda:0'), False, False)
    frame = np.full((640, 640, 3), 127, dtype=np.uint8)
    for i in range(5):
        tracks = tracker.update(np.array([[100+i, 100, 200+i, 300, 0.95, 0.0]]), frame)
    assert tracks.ndim == 2 and tracks.shape[1] >= 6, (name, tracks.shape)
    results[name] = list(tracks.shape)
sample = Path('/tmp/day22_smoke_frames')
sample.mkdir(exist_ok=False)
for i in range(5):
    cv2.imwrite(str(sample / f'{i+1:06d}.jpg'), np.zeros((640, 640, 3), dtype=np.uint8))
import subprocess, sys
for name in ['bytetrack', 'botsort']:
    command = [sys.executable, 'scripts/run_tracking.py', '--source', str(sample),
        '--seq-name', 'kiem_thu', '--tracker', name, '--device', 'cuda:0',
        '--out', str(Path('/tmp') / ('day22_smoke_' + name)), '--save-video']
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert '-> 5 frame ' in result.stdout, result.stdout
    print(result.stdout)
Path('preflight.json').write_text(json.dumps({'gpu': torch.cuda.get_device_name(), 'trackers': results, 'status': 'passed'}, indent=2))
print(results)
"""
subprocess.run([PYTHON, '-c', smoke_code], check=True)
trackeval = Path('/tmp/day22_trackeval_smoke')
subprocess.run(['git', 'clone', 'https://github.com/JonathonLuiten/TrackEval.git', str(trackeval)], check=True)
subprocess.run([PYTHON, '-m', 'pip', 'install', '--no-deps', '-e', str(trackeval)], check=True)
practice = Path('/tmp/day22_eval_smoke/video_1')
(practice / 'gt').mkdir(parents=True)
rows = '\\n'.join(f'{i},1,10,10,30,60,1,1,1' for i in range(1, 6)) + '\\n'
(practice / 'gt/gt.txt').write_text(rows)
(practice / 'seqinfo.ini').write_text('[Sequence]\\nname=video_1\\nimDir=img1\\nframeRate=20\\nseqLength=5\\nimWidth=640\\nimHeight=640\\nimExt=.jpg\\n')
(practice / 'eval_config.json').write_text(json.dumps({'benchmark': 'LAB', 'split': 'train'}))
submission = practice.parent / 'video_1.txt'
submission.write_text('\\n'.join(f'{i},1,10,10,30,60,1,-1,-1,-1' for i in range(1, 6)) + '\\n')
with (WORK / 'preflight_trackeval.log').open('w') as log:
    subprocess.run([PYTHON, 'scripts/evaluate_practice.py', '--trackeval-root', str(trackeval),
        '--lab-data-root', str(practice.parent), '--submission', str(submission), '--run-name', 'smoke'],
        stdout=log, stderr=subprocess.STDOUT, check=True)
(WORK / 'trackeval_preflight_passed.txt').write_text('Kiểm tra tương thích bằng dữ liệu tổng hợp; không phải metric bài lab.\\n')
'''
        cells.append({"cell_type": "code", "metadata": {}, "source": smoke.splitlines(True), "outputs": [], "execution_count": None})
    else:
        code = ""
        if args.selections:
            choices = json.loads(args.selections.read_text())
            code += "(WORK / 'selections.json').write_text(" + repr(json.dumps(choices)) + ")\n"
            code += "os.environ['LAB_MODE'] = 'final'\n"
        code += "subprocess.run([PYTHON, 'scripts/kaggle_lab_pipeline.py'], check=True)\n"
        cells.append({"cell_type": "code", "metadata": {}, "source": code.splitlines(True), "outputs": [], "execution_count": None})
    notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 4}
    (target / "day22.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2))
    slug = "track4-day22-tracking" + ("-preflight" if args.preflight else "")
    metadata = {"id": args.owner + "/" + slug, "title": "Track4 Day22 Tracking" + (" Preflight" if args.preflight else ""),
        "code_file": "day22.ipynb", "language": "python", "kernel_type": "notebook",
        "is_private": True, "enable_gpu": True, "enable_internet": True,
        "dataset_sources": [args.dataset] if args.dataset else [], "competition_sources": [],
        "kernel_sources": [] if args.preflight else [args.owner + '/track4-day22-tracking-preflight']}
    (target / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2))
    print(f"Đã tạo notebook tại {target}")


if __name__ == "__main__":
    main()
