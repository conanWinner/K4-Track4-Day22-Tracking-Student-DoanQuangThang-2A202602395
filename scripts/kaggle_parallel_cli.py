"""Chạy CLI Kaggle hiện có, upload các phần nhỏ bằng bốn kết nối độc lập."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi, ResumableUploadContext
from kaggle.cli import main


class RetainedUploadContext(ResumableUploadContext):
    """Giữ metadata upload để không xóa dữ liệu tạm khi context kết thúc."""

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Kết thúc context mà không xóa metadata của lượt upload.

        Args:
            exc_type: Loại ngoại lệ, nếu có.
            exc_value: Ngoại lệ, nếu có.
            exc_traceback: Traceback, nếu có.

        Returns:
            False để truyền ngoại lệ ra ngoài context.
        """
        return False


def upload_one(api, folder, name, blob_type, resources):
    """Upload một phần qua API của chính package CLI đang cài.

    Args:
        api: Client đã xác thực của CLI.
        folder: Thư mục staging.
        name: Tên tệp dữ liệu.
        blob_type: Loại blob do CLI chọn.
        resources: Metadata tài nguyên của CLI.

    Returns:
        Đối tượng file của request tạo dataset.

    Raises:
        RuntimeError: Khi một phần không upload thành công.
    """
    # Không xóa metadata upload tạm khi kết thúc context.
    with RetainedUploadContext() as context:
        uploaded = api._upload_file(name, str(Path(folder) / name), blob_type, context, True, resources)
    if uploaded is None:
        raise RuntimeError(f'Upload thất bại: {name}')
    return api._new_file(uploaded)


def parallel_upload_files(api, request, resources, folder, blob_type, upload_context,
                          quiet=False, dir_mode='skip', ignore_patterns=None):
    """Upload staging các phần nhỏ, chỉ tạo dataset khi tất cả thành công.

    Args:
        api: Client CLI đã xác thực.
        request: Request tạo dataset của CLI.
        resources: Metadata tệp.
        folder: Thư mục chứa manifest, các phần và metadata dataset.
        blob_type: Loại blob do CLI chọn.
        upload_context: Context của CLI, không dùng để xóa tệp.
        quiet: Tham số giữ nguyên giao diện CLI.
        dir_mode: Tham số giữ nguyên giao diện CLI.
        ignore_patterns: Tham số giữ nguyên giao diện CLI.

    Raises:
        ValueError: Khi staging chứa tệp ngoài manifest và các phần dữ liệu.
    """
    paths = sorted(Path(folder).iterdir())
    files = [p for p in paths if p.name != 'dataset-metadata.json']
    if any(not p.is_file() or not (p.name == 'data_parts.json' or p.name.endswith('.bin')) for p in files):
        raise ValueError('Staging chỉ được chứa manifest và các phần .bin.')
    with ThreadPoolExecutor(max_workers=4) as executor:
        pending = {executor.submit(upload_one, api, folder, p.name, blob_type, resources): p.name for p in files}
        for index, future in enumerate(as_completed(pending), 1):
            request.files.append(future.result())
            print(f'Đã upload {index}/{len(files)}: {pending[future]}', flush=True)


if __name__ == '__main__':
    KaggleApi.upload_files = parallel_upload_files
    main()
