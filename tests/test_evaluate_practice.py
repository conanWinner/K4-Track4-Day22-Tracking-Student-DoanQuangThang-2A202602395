"""Kiểm tra tiến trình chấm nhận bản vá NumPy và đúng video luyện."""

from pathlib import Path

from evaluate_practice import _load_eval_config, run_trackeval, stage


def test_subprocess_receives_compatibility_patch(monkeypatch):
    """Bản vá phải chạy trong tiến trình con, trước khi nạp TrackEval."""
    calls = []
    monkeypatch.setattr("evaluate_practice.subprocess.run", lambda cmd, **kw: calls.append((cmd, kw)))
    run_trackeval(Path("/tmp/trackeval"), "thu_01", "lab", "train")
    cmd, options = calls[0]
    assert cmd[1] == "-c"
    assert "np.float = float; np.int = int" in cmd[2]
    assert "runpy.run_path" in cmd[2]
    assert cmd[3].endswith("scripts/run_mot_challenge.py")
    assert cmd[cmd.index("--SEQ_INFO") + 1] == "video_1"
    assert options == {"check": True}


def test_stage_respects_configured_split(tmp_path):
    """Nhãn và dự đoán phải nằm đúng nhánh mà tiến trình chấm đọc."""
    lab = tmp_path / "lab"
    video = lab / "video_1"
    (video / "gt").mkdir(parents=True)
    (video / "gt/gt.txt").write_text("nhãn thử")
    (video / "seqinfo.ini").write_text("cấu hình thử")
    submission = tmp_path / "video_1.txt"
    submission.write_text("kết quả thử")
    root = tmp_path / "trackeval"
    stage(root, lab, submission, "thu_01", "LAB", "validation")
    assert (root / "data/gt/mot_challenge/LAB-validation/video_1/gt/gt.txt").read_text() == "nhãn thử"
    assert (root / "data/trackers/mot_challenge/LAB-validation/thu_01/data/video_1.txt").read_text() == "kết quả thử"


def test_missing_eval_config_uses_generic_benchmark(tmp_path):
    """Gói giảng viên thiếu JSON vẫn chấm được bằng cây thư mục chuẩn."""
    assert _load_eval_config(tmp_path) == {"benchmark": "LAB", "split": "train"}


def test_existing_eval_config_is_preserved(tmp_path):
    """Cấu hình có sẵn trong gói luôn được ưu tiên hơn cấu hình dự phòng."""
    video = tmp_path / "video_1"
    video.mkdir()
    (video / "eval_config.json").write_text('{"benchmark": "LAB_CUSTOM", "split": "validation"}')
    assert _load_eval_config(tmp_path) == {"benchmark": "LAB_CUSTOM", "split": "validation"}
