from io import BytesIO

from PIL import Image


def _process(
    data: bytes,
    target_w: int | None = None,
    target_h: int | None = None,
    crop_ratio: tuple[int, int] | None = None,
    max_longest: int | None = None,
    jpeg_quality: int = 85,
) -> bytes:
    img = Image.open(BytesIO(data))
    if img.mode in ("P", "RGBA", "LA"):
        img = img.convert("RGB")

    if crop_ratio:
        cw, ch = crop_ratio
        iw, ih = img.size
        target_ratio = cw / ch
        current_ratio = iw / ih
        if current_ratio > target_ratio:
            new_w = int(ih * target_ratio)
            offset = (iw - new_w) // 2
            img = img.crop((offset, 0, offset + new_w, ih))
        elif current_ratio < target_ratio:
            new_h = int(iw / target_ratio)
            offset = (ih - new_h) // 2
            img = img.crop((0, offset, iw, offset + new_h))

    if target_w and target_h:
        img = img.resize((target_w, target_h), Image.LANCZOS)
    elif max_longest:
        iw, ih = img.size
        if iw > ih and iw > max_longest:
            new_w = max_longest
            new_h = int(ih * (max_longest / iw))
            img = img.resize((new_w, new_h), Image.LANCZOS)
        elif ih > max_longest:
            new_h = max_longest
            new_w = int(iw * (max_longest / ih))
            img = img.resize((new_w, new_h), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
    return buf.getvalue()


def process_gallery(data: bytes) -> bytes:
    return _process(data, crop_ratio=(4, 3), max_longest=1200)


def process_avatar(data: bytes) -> bytes:
    return _process(data, target_w=400, target_h=400, crop_ratio=(1, 1))


def process_squad_card(data: bytes) -> bytes:
    return _process(data, target_w=600, target_h=800, crop_ratio=(3, 4))


def process_cover(data: bytes) -> bytes:
    return _process(data, target_w=1920, target_h=1080, crop_ratio=(16, 9))


def process_update_image(data: bytes) -> bytes:
    return _process(data, max_longest=1200)
