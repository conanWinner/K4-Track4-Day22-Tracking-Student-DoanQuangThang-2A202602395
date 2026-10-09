"""Kiểm tra tính toàn vẹn khi chia và ghép byte, không cần dữ liệu lab."""

import pytest

from archive_parts import assemble_archive, split_archive


def test_roundtrip_keeps_original_bytes(tmp_path):
    source = tmp_path / 'source.zip'
    data = bytes(range(256)) * 3
    source.write_bytes(data)
    staging = tmp_path / 'parts'
    staging.mkdir()
    manifest = split_archive(source, staging, 100)
    assert len(manifest['parts']) == 8
    result = tmp_path / 'joined.zip'
    assemble_archive(staging / 'data_parts.json', result)
    assert result.read_bytes() == data
    assert source.read_bytes() == data


def test_corrupted_part_is_rejected(tmp_path):
    source = tmp_path / 'source.zip'
    source.write_bytes(b'abcdef')
    staging = tmp_path / 'parts'
    staging.mkdir()
    manifest = split_archive(source, staging, 3)
    (staging / manifest['parts'][0]['name']).write_bytes(b'xyz')
    with pytest.raises(ValueError, match='checksum'):
        assemble_archive(staging / 'data_parts.json', tmp_path / 'joined.zip')


def test_join_preserves_existing_destination(tmp_path):
    source = tmp_path / 'source.zip'
    source.write_bytes(b'abc')
    staging = tmp_path / 'parts'
    staging.mkdir()
    split_archive(source, staging, 10)
    destination = tmp_path / 'joined.zip'
    destination.write_bytes(b'preserve')
    with pytest.raises(FileExistsError):
        assemble_archive(staging / 'data_parts.json', destination)
    assert destination.read_bytes() == b'preserve'
