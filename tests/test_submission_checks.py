"""Kiểm tra bộ xác minh bài nộp bằng dữ liệu nhỏ, không cần ảnh lab."""

import pytest

from submission_checks import parse_metric_summary, validate_mot_rows, validate_zip_members


def test_safe_archive():
    validate_zip_members(['lab_data/video_1/img1/000001.jpg'])


@pytest.mark.parametrize('names', [['../outside'], ['/outside'], ['a\\b'], ['C:/outside'], ['a', 'a']])
def test_unsafe_archive(names):
    with pytest.raises(ValueError):
        validate_zip_members(names)


def test_frames_without_tracks_do_not_require_rows():
    assert validate_mot_rows('1,1,10,20,30,40,0.9,-1,-1,-1\n', 100) == 1


@pytest.mark.parametrize('content', ['', '1,2', '101,1,0,0,10,20,.9,-1,-1,-1',
    '1,1,0,0,-10,20,.9,-1,-1,-1', '1,1,nan,0,10,20,.9,-1,-1,-1',
    '1,1,0,0,10,20,.9,-1,-1,-1\n1,1,0,0,10,20,.9,-1,-1,-1'])
def test_bad_results(content):
    with pytest.raises(ValueError):
        validate_mot_rows(content, 100)


def test_metric_summary_keeps_percentage_scale():
    assert parse_metric_summary('HOTA MOTA IDF1 DetA\n60.5 -10 70.2 55\n') == {
        'HOTA': 60.5, 'MOTA': -10.0, 'IDF1': 70.2}


@pytest.mark.parametrize('content', ['HOTA MOTA\n60 70', 'HOTA MOTA IDF1\n1 2',
    'HOTA MOTA IDF1\nnan 3 4', 'HOTA MOTA IDF1\n101 3 4'])
def test_invalid_metric_summary(content):
    with pytest.raises(ValueError):
        parse_metric_summary(content)
