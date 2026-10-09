"""Đọc log phiên Kaggle trong thời gian hữu hạn và giữ bản sao mới."""

import argparse
import json
import signal
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelSessionLogsStreamRequest


def main() -> None:
    """Lưu log trực tiếp, không ghi đè tệp hoặc thay đổi phiên chạy từ xa."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=35)
    args = parser.parse_args()
    owner, slug = args.kernel.split('/')
    api = KaggleApi()
    api.authenticate()
    request = ApiGetKernelSessionLogsStreamRequest()
    request.user_name = owner
    request.kernel_slug = slug
    request.wait_for_logs_url_seconds = 5
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as saved, api.build_kaggle_client() as client:
        response = client.kernels.kernels_api_client.get_kernel_session_logs_stream(request)
        print('Loại log:', response.headers.get('Content-Type'), flush=True)
        messages = []
        signal.signal(signal.SIGALRM, signal.default_int_handler)
        signal.alarm(args.seconds)
        try:
            for raw in response.iter_lines(chunk_size=1):
                line = raw.decode('utf-8', 'replace')
                saved.write(line + '\n')
                saved.flush()
                if line.startswith('data: '):
                    try:
                        message = json.loads(line[6:]).get('data', '')
                    except (ValueError, AttributeError):
                        continue
                    if any(word in message for word in ['Đang thử', 'Đang chạy đủ', 'Đã chạy', 'Error', 'Traceback']):
                        messages.append(message.strip())
        except KeyboardInterrupt:
            pass
        finally:
            signal.alarm(0)
            response.close()
        print('\n'.join(messages[-12:]))


if __name__ == '__main__':
    main()
