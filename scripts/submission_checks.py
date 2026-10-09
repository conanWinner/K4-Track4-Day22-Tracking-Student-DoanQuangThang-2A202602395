"""Kiểm tra an toàn ZIP và định dạng kết quả MOT, không cần GPU."""

import math
from pathlib import PurePosixPath


def validate_zip_members(names: list[str]) -> None:
    """Từ chối đường dẫn ZIP có thể thoát khỏi thư mục giải nén.

    Args:
        names: Danh sách đường dẫn thành viên ZIP.

    Raises:
        ValueError: Khi có đường dẫn tuyệt đối, đi ngược hoặc trùng nhau.
    """
    if len(set(names)) != len(names):
        raise ValueError('ZIP có đường dẫn trùng nhau.')
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
            raise ValueError(f'Đường dẫn ZIP không hợp lệ: {name}')


def validate_mot_rows(content: str, frame_count: int) -> int:
    """Kiểm tra mười cột MOT và tính duy nhất của mỗi ID trong một frame.

    Args:
        content: Nội dung file kết quả.
        frame_count: Số frame đã xử lý, không phải số dòng kết quả.

    Returns:
        Số dòng track hợp lệ.

    Raises:
        ValueError: Khi file rỗng hoặc có dòng không hợp lệ.
    """
    seen = set()
    lines = content.strip().splitlines()
    if not lines:
        raise ValueError('File kết quả rỗng, cần kiểm tra trực tiếp.')
    for line in lines:
        fields = line.split(',')
        if len(fields) != 10:
            raise ValueError('Kết quả MOT phải có mười cột.')
        values = [float(field) for field in fields]
        if not all(math.isfinite(value) for value in values):
            raise ValueError('Kết quả có NaN hoặc vô cực.')
        frame, track_id = values[:2]
        if frame != int(frame) or not 1 <= frame <= frame_count or track_id != int(track_id) or track_id < 1:
            raise ValueError('Frame hoặc ID không hợp lệ.')
        if values[4] <= 0 or values[5] <= 0 or not 0 <= values[6] <= 1:
            raise ValueError('Kích thước hộp hoặc confidence không hợp lệ.')
        key = (int(frame), int(track_id))
        if key in seen:
            raise ValueError('Một ID xuất hiện hai lần trong cùng frame.')
        seen.add(key)
    return len(lines)


def parse_metric_summary(content: str) -> dict[str, float]:
    """Đọc ba metric bắt buộc từ bảng summary do TrackEval xuất.

    Args:
        content: Hai dòng tiêu đề và giá trị của pedestrian_summary.txt.

    Returns:
        HOTA, MOTA và IDF1 theo thang phần trăm của TrackEval.

    Raises:
        ValueError: Khi thiếu cột, sai số cột hoặc có số không hợp lệ.
    """
    lines = [line for line in content.splitlines() if line.strip()]
    if len(lines) != 2:
        raise ValueError('Summary TrackEval phải có đúng hai dòng.')
    header, values = lines[0].split(), lines[1].split()
    if len(header) != len(values):
        raise ValueError('Summary lệch số cột.')
    fields = dict(zip(header, values))
    if not {'HOTA', 'MOTA', 'IDF1'} <= fields.keys():
        raise ValueError('Summary thiếu HOTA, MOTA hoặc IDF1.')
    metrics = {key: float(fields[key]) for key in ['HOTA', 'MOTA', 'IDF1']}
    if not all(math.isfinite(value) for value in metrics.values()):
        raise ValueError('Metric không hữu hạn.')
    if not 0 <= metrics['HOTA'] <= 100 or not 0 <= metrics['IDF1'] <= 100 or metrics['MOTA'] > 100:
        raise ValueError('Metric vượt thang phần trăm hợp lệ.')
    return metrics
