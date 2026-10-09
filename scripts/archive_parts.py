"""Chia và ghép ZIP theo byte, xác minh checksum từng phần và toàn bộ."""

import hashlib
import json
from pathlib import Path

from submission_checks import validate_zip_members


def split_archive(archive: Path, destination: Path, part_bytes: int) -> dict:
    """Ghi các phần mới và manifest, giữ nguyên tệp nguồn.

    Args:
        archive: ZIP gốc.
        destination: Thư mục staging đã tạo.
        part_bytes: Số byte tối đa của một phần.

    Returns:
        Manifest chứa kích thước và SHA-256.

    Raises:
        ValueError: Khi kích thước phần không dương.
        FileExistsError: Khi đích đã có tệp cùng tên.
    """
    if part_bytes <= 0:
        raise ValueError('Kích thước phần phải dương.')
    parts = []
    digest = hashlib.sha256()
    with archive.open('rb') as source:
        while data := source.read(part_bytes):
            name = f'data_lab21.zip.part{len(parts):04d}.bin'
            with (destination / name).open('xb') as target:
                target.write(data)
            digest.update(data)
            parts.append({'name': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    manifest = {'bytes': archive.stat().st_size, 'sha256': digest.hexdigest(), 'parts': parts}
    with (destination / 'data_parts.json').open('x') as target:
        json.dump(manifest, target, indent=2)
    return manifest


def assemble_archive(manifest_path: Path, destination: Path) -> None:
    """Ghép vào tệp mới và kiểm tra từng phần cùng checksum ZIP gốc.

    Args:
        manifest_path: JSON đi cùng các phần dữ liệu.
        destination: ZIP mới, chưa tồn tại.

    Raises:
        ValueError: Khi đường dẫn, kích thước hoặc checksum không hợp lệ.
        FileExistsError: Khi ZIP đích đã tồn tại.
    """
    manifest = json.loads(manifest_path.read_text())
    validate_zip_members([part['name'] for part in manifest['parts']])
    digest = hashlib.sha256()
    total = 0
    with destination.open('xb') as target:
        for part in manifest['parts']:
            data = (manifest_path.parent / part['name']).read_bytes()
            if len(data) != part['bytes'] or hashlib.sha256(data).hexdigest() != part['sha256']:
                raise ValueError(f"Phần dữ liệu lỗi checksum: {part['name']}")
            target.write(data)
            digest.update(data)
            total += len(data)
    if total != manifest['bytes'] or digest.hexdigest() != manifest['sha256']:
        raise ValueError('ZIP ghép không khớp checksum gốc.')
