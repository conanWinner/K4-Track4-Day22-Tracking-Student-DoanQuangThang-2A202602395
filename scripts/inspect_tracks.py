"""Tạo bảng ảnh có ID từ kết quả MOT để so sánh trực quan các cấu hình."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    """Vẽ các frame được chỉ định, giữ nguyên ảnh và kết quả nguồn.

    Raises:
        FileExistsError: Khi ảnh đích đã tồn tại.
        ValueError: Khi chỉ số frame vượt số ảnh của video.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab-data-root', required=True, type=Path)
    parser.add_argument('--video', required=True)
    parser.add_argument('--result', required=True, action='append', type=Path)
    parser.add_argument('--frames', default='1,50,100,150')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    frames = [int(value) for value in args.frames.split(',')]
    images = sorted((args.lab_data_root / args.video / 'img1').glob('*.jpg'))
    if any(frame < 1 or frame > len(images) for frame in frames):
        raise ValueError('Frame vượt phạm vi video.')
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    sheet = Image.new('RGB', (640 * len(frames), 400 * len(args.result)), 'white')
    for row, result in enumerate(args.result):
        records = {}
        for line in result.read_text().splitlines():
            fields = line.split(',')
            frame = int(fields[0])
            if frame in frames:
                records.setdefault(frame, []).append([float(value) for value in fields[:7]])
        for column, frame in enumerate(frames):
            original = Image.open(images[frame - 1]).convert('RGB')
            scale = min(640 / original.width, 360 / original.height)
            tile = original.resize((round(original.width * scale), round(original.height * scale)))
            draw = ImageDraw.Draw(tile)
            for values in records.get(frame, []):
                _, track_id, x, y, width, height, confidence = values
                rng = np.random.default_rng(int(track_id) * 9973 + 17)
                color = tuple(int(value) for value in rng.integers(64, 255, size=3)[::-1])
                box = (x * scale, y * scale, (x + width) * scale, (y + height) * scale)
                draw.rectangle(box, outline=color, width=2)
                if height * scale >= 15:
                    draw.text((max(0, x * scale), max(0, y * scale - 15)), str(int(track_id)),
                              font=font, fill=color, stroke_width=1, stroke_fill='black')
            x0, y0 = column * 640, row * 400
            sheet.paste(tile, (x0, y0 + 35))
            ImageDraw.Draw(sheet).text((x0 + 5, y0 + 5),
                f'{result.parent.name} | frame {frame}', font=font, fill='black')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f'Đã lưu ảnh so sánh: {args.output}')


if __name__ == '__main__':
    main()
