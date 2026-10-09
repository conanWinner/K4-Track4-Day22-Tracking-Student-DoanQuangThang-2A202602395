"""Kiểm tra context giữ metadata, không cần cài hoặc kết nối Kaggle."""

import ast
from pathlib import Path

import pytest


def _context_type():
    """Nạp riêng lớp context với lớp nền giả không thực hiện xóa tệp."""
    class FakeContext:
        cleaned = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.cleaned = True

    source = Path(__file__).resolve().parents[1] / 'scripts/kaggle_parallel_cli.py'
    tree = ast.parse(source.read_text())
    definition = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                      and node.name == 'RetainedUploadContext')
    namespace = {'ResumableUploadContext': FakeContext}
    module = ast.Module(body=[definition], type_ignores=[])
    exec(compile(module, str(source), 'exec'), namespace)
    return namespace['RetainedUploadContext']


def test_success_does_not_clean_upload_metadata():
    context = _context_type()()
    with context:
        pass
    assert context.cleaned is False


def test_upload_error_is_not_suppressed():
    context = _context_type()()
    with pytest.raises(RuntimeError, match='lỗi upload'):
        with context:
            raise RuntimeError('lỗi upload')
    assert context.cleaned is False
