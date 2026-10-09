"""Chuẩn bị thư mục upload riêng, giữ nguyên ZIP gốc và kiểm tra gói lab."""

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from submission_checks import validate_zip_members
from archive_parts import split_archive


def main() -> None:
    """Kiểm tra ZIP và tạo staging mới chỉ gồm gói dữ liệu và metadata."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--owner', required=True)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--part-size-mb', type=int, default=0)
    args = parser.parse_args()
    counts = {}
    with zipfile.ZipFile(args.archive) as archive:
        names = archive.namelist()
        validate_zip_members(names)
        for index in range(1, 6):
            video = f'video_{index}'
            images = [name for name in names if f'{video}/img1/' in name
                      and name.endswith('.jpg') and Path(name).stem.isdecimal()
                      and not name.startswith('__MACOSX/')]
            if not images:
                raise ValueError(f'Thiếu ảnh {video}')
            counts[video] = len(images)
            if index > 1 and any(name.endswith(f'{video}/gt/gt.txt') for name in names):
                raise ValueError('Gói học viên không được có nhãn video_2–video_5.')
        for required in ['video_1/gt/gt.txt', 'video_1/seqinfo.ini']:
            if not any(name.endswith(required) for name in names):
                raise ValueError(f'Thiếu {required}')
        if not any(name.endswith('video_1/eval_config.json') for name in names):
            print('Gói thiếu eval_config.json; script chấm sẽ dùng benchmark LAB, split train.')
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f'ZIP lỗi CRC: {corrupt}')
    args.out.mkdir(parents=True, exist_ok=False)
    if args.part_size_mb:
        manifest = split_archive(args.archive, args.out, args.part_size_mb * 1024 * 1024)
        print(f"Đã chia thành {len(manifest['parts'])} phần, giữ nguyên ZIP gốc.")
    else:
        shutil.copy2(args.archive, args.out / 'data_lab21.zip')
    metadata = {'title': 'Track4 Day22 Tracking Lab Data', 'id': args.owner + '/track4-day22-tracking-lab-data',
        'licenses': [{'name': 'unknown'}],
        'description': 'Gói dữ liệu giảng viên phát cho bài lab tracking. Dùng riêng tư cho học tập; không xác định giấy phép phân phối lại.'}
    (args.out / 'dataset-metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    digest = hashlib.file_digest(args.archive.open('rb'), 'sha256').hexdigest()
    print(json.dumps({'frames': counts, 'bytes': args.archive.stat().st_size, 'sha256': digest,
        'upload_directory': str(args.out)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
