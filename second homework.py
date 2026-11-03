import cv2
print("太棒了！OpenCV 安装成功！")
print("当前 OpenCV 版本号是:", cv2.__version__)


# ====== get_image_info：读取并显示图片基本信息 ======

"""使用 OpenCV 读取图片并输出基本信息的小工具。"""

import os

import cv2

# 常见图片格式的文件头（魔数），比只看扩展名更可靠
_MAGIC_SIGNATURES = (
    (b"\xff\xd8\xff", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"GIF87a", "GIF"),
    (b"GIF89a", "GIF"),
    (b"BM", "BMP"),
    (b"II*\x00", "TIFF"),
    (b"MM\x00*", "TIFF"),
)


def _detect_format(image_path):
    """根据文件头判断真实格式，无法识别时退回扩展名。"""
    try:
        with open(image_path, "rb") as f:
            header = f.read(32)
    except OSError:
        header = b""

    for magic, name in _MAGIC_SIGNATURES:
        if header.startswith(magic):
            return name

    # WEBP 的魔数是 RIFF....WEBP，需要检查偏移 8 处的标记
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return "WEBP"

    # 兜底：使用扩展名（去掉点并大写）
    ext = os.path.splitext(image_path)[1].lstrip(".").upper()
    return ext or "未知"


def _format_file_size(size_bytes):
    """把字节数转换成 KB 或 MB，保留 2 位小数。"""
    kb = size_bytes / 1024
    if kb < 1024:
        return f"{kb:.2f} KB"
    return f"{kb / 1024:.2f} MB"


def get_image_info(image_path):
    """
    读取图片并打印 / 返回基本信息。

    返回:
        dict: 成功时返回包含文件信息的字典；失败时返回 None。
    """
    # 1. 基础校验：路径存在且是普通文件
    if not os.path.exists(image_path):
        print(f"[错误] 文件不存在：{image_path}")
        return None
    if not os.path.isfile(image_path):
        print(f"[错误] 这不是一个文件：{image_path}")
        return None

    file_size = os.path.getsize(image_path)
    if file_size == 0:
        print(f"[错误] 文件为空，不是有效图片：{image_path}")
        return None

    # 2. 读取图片。IMREAD_UNCHANGED 会保留 alpha 通道，便于判断 RGBA
    try:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    except cv2.error as exc:  # OpenCV 内部解码异常
        print(f"[错误] 图片读取失败（文件可能已损坏）：{image_path}\n        {exc}")
        return None

    if image is None:
        print(f"[错误] 无法解析为图片，请确认文件格式是否受支持：{image_path}")
        return None

    # 3. 提取尺寸和颜色模式
    # OpenCV 内部按 BGR/BGRA 存储，这里按用户习惯统一称为 RGB/RGBA
    height, width = image.shape[:2]
    channels = 1 if image.ndim == 2 else image.shape[2]
    color_mode = {1: "灰度", 3: "RGB", 4: "RGBA"}.get(channels, f"{channels} 通道")

    info = {
        "file_name": os.path.basename(image_path),
        "format": _detect_format(image_path),
        "width": width,
        "height": height,
        "color_mode": color_mode,
        "file_size": _format_file_size(file_size),
        "file_size_bytes": file_size,
    }

    # 4. 打印结果
    print(f"文件名   : {info['file_name']}")
    print(f"格式     : {info['format']}")
    print(f"尺寸     : {info['width']} x {info['height']} 像素")
    print(f"颜色模式 : {info['color_mode']}")
    print(f"文件大小 : {info['file_size']}")

    return info


# ====== 图片编辑功能 ======


def _load_image(image_path):
    """读取图片，失败时给出提示并返回 None。"""
    if not os.path.exists(image_path):
        print(f"[错误] 文件不存在：{image_path}")
        return None
    if not os.path.isfile(image_path):
        print(f"[错误] 这不是一个文件：{image_path}")
        return None
    if os.path.getsize(image_path) == 0:
        print(f"[错误] 文件为空，不是有效图片：{image_path}")
        return None

    try:
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    except cv2.error as exc:
        print(f"[错误] 图片读取失败（文件可能已损坏）：{image_path}\n        {exc}")
        return None

    if image is None:
        print(f"[错误] 无法解析为图片，请确认文件格式是否受支持：{image_path}")
        return None
    return image


def _unique_output_path(path):
    """目标文件已存在时自动加序号，避免覆盖已有文件。"""
    if not os.path.exists(path):
        return path

    folder, name = os.path.split(path)
    stem, ext = os.path.splitext(name)
    index = 1
    while os.path.exists(os.path.join(folder, f"{stem}_{index}{ext}")):
        index += 1
    return os.path.join(folder, f"{stem}_{index}{ext}")


def _save_image(image, image_path, suffix, output_path=None):
    """
    保存处理后的图片，绝不覆盖原图。

    - 未指定 output_path：在原图旁边生成带后缀的新文件
    - 目标文件已存在：自动加序号，不覆盖旧结果
    返回实际保存路径；失败时返回 None。
    """
    if output_path is None:
        stem, ext = os.path.splitext(image_path)
        target = f"{stem}{suffix}{ext or '.png'}"
    else:
        target = output_path
        # 明确拒绝覆盖原图
        if os.path.abspath(target) == os.path.abspath(image_path):
            print("[错误] 输出路径不能与原图相同，已取消保存（不会覆盖原图）。")
            return None

    target = _unique_output_path(target)

    # JPEG 不支持透明通道，保存前给出提示
    if image.ndim == 3 and image.shape[2] == 4 and \
            os.path.splitext(target)[1].lower() in (".jpg", ".jpeg"):
        print("[提示] JPEG 不支持透明通道，保存后 alpha 通道会丢失。")

    try:
        ok = cv2.imwrite(target, image)
    except cv2.error as exc:
        print(f"[错误] 保存失败：{target}\n        {exc}")
        return None

    if not ok:
        print(f"[错误] 保存失败，请检查目录是否存在、扩展名是否受支持：{target}")
        return None

    print(f"[完成] 已保存：{target}")
    return target


def resize_image(image_path, width=None, height=None, output_path=None):
    """
    缩放图片。

    - width、height 都指定：严格缩放到该尺寸（可能改变宽高比）
    - 只指定其中一个：按原图比例自动计算另一个
    - 都不指定：提示错误

    返回保存路径；失败时返回 None。
    """
    image = _load_image(image_path)
    if image is None:
        return None

    if width is None and height is None:
        print("[错误] 请至少指定 width 或 height 其中一个。")
        return None

    # 统一转成正整数，避免把 0、负数或非数字传给 OpenCV
    try:
        if width is not None:
            width = int(width)
            if width <= 0:
                raise ValueError
        if height is not None:
            height = int(height)
            if height <= 0:
                raise ValueError
    except (TypeError, ValueError):
        print("[错误] 宽和高必须是大于 0 的整数。")
        return None

    old_h, old_w = image.shape[:2]

    if width is not None and height is not None:
        new_w, new_h = width, height
    elif width is not None:
        # 只给宽度：按比例算高度
        new_w = width
        new_h = max(1, round(old_h * width / old_w))
    else:
        # 只给高度：按比例算宽度
        new_h = height
        new_w = max(1, round(old_w * height / old_h))

    # 缩小时用 INTER_AREA 更清晰，放大时用 INTER_LINEAR 更平滑
    interpolation = cv2.INTER_AREA if new_w * new_h < old_w * old_h else cv2.INTER_LINEAR
    resized = cv2.resize(image, (new_w, new_h), interpolation=interpolation)

    print(f"[信息] 缩放：{old_w}x{old_h} -> {new_w}x{new_h}")
    return _save_image(resized, image_path, f"_resized_{new_w}x{new_h}", output_path)


def crop_image(image_path, left, top, right, bottom, output_path=None):
    """
    裁剪图片，坐标为（左、上、右、下），right / bottom 为不包含的边界。
    坐标越界或无效时提示并返回 None。
    """
    image = _load_image(image_path)
    if image is None:
        return None

    old_h, old_w = image.shape[:2]

    try:
        left, top, right, bottom = int(left), int(top), int(right), int(bottom)
    except (TypeError, ValueError):
        print("[错误] 裁剪坐标必须是整数：left, top, right, bottom。")
        return None

    # 必须满足 0 <= left < right <= 宽，0 <= top < bottom <= 高
    if not (0 <= left < right <= old_w and 0 <= top < bottom <= old_h):
        print(
            f"[错误] 裁剪坐标越界或无效：({left}, {top}, {right}, {bottom})，"
            f"原图尺寸为 {old_w}x{old_h}。\n"
            f"        要求 0 <= left < right <= {old_w} 且 0 <= top < bottom <= {old_h}。"
        )
        return None

    cropped = image[top:bottom, left:right]

    print(
        f"[信息] 裁剪区域：left={left}, top={top}, right={right}, bottom={bottom}，"
        f"结果尺寸：{cropped.shape[1]}x{cropped.shape[0]}"
    )
    return _save_image(
        cropped, image_path, f"_cropped_{left}_{top}_{right}_{bottom}", output_path
    )


def rotate_image(image_path, angle, output_path=None):
    """
    旋转图片，angle 仅支持 90、180、270。
    90 度为顺时针，270 度为逆时针（等于顺时针 270 度）。
    """
    image = _load_image(image_path)
    if image is None:
        return None

    try:
        angle = int(angle)
    except (TypeError, ValueError):
        print("[错误] 旋转角度必须是 90、180 或 270。")
        return None

    rotate_codes = {
        90: cv2.ROTATE_90_CLOCKWISE,
        180: cv2.ROTATE_180,
        270: cv2.ROTATE_90_COUNTERCLOCKWISE,
    }
    if angle not in rotate_codes:
        print(f"[错误] 不支持的角度：{angle}。仅支持 90、180、270 度。")
        return None

    rotated = cv2.rotate(image, rotate_codes[angle])
    print(
        f"[信息] 旋转 {angle} 度：{image.shape[1]}x{image.shape[0]} -> "
        f"{rotated.shape[1]}x{rotated.shape[0]}"
    )
    return _save_image(rotated, image_path, f"_rotated_{angle}", output_path)


def flip_image(image_path, direction="horizontal", output_path=None):
    """
    翻转图片。

    direction 可选：
    - "horizontal" / "h" / "水平"：左右镜像
    - "vertical"   / "v" / "垂直"：上下翻转
    """
    image = _load_image(image_path)
    if image is None:
        return None

    key = str(direction).strip().lower()
    if key in ("horizontal", "h", "水平", "左右"):
        flip_code, label, suffix = 1, "水平", "_flipped_h"
    elif key in ("vertical", "v", "垂直", "上下"):
        flip_code, label, suffix = 0, "垂直", "_flipped_v"
    else:
        print(
            f"[错误] 不支持的翻转方向：{direction}。"
            "可选 horizontal（水平）或 vertical（垂直）。"
        )
        return None

    flipped = cv2.flip(image, flip_code)
    print(f"[信息] 已{label}翻转：{image.shape[1]}x{image.shape[0]}")
    return _save_image(flipped, image_path, suffix, output_path)


if __name__ == "__main__":
    import sys

    # 保持原来的用法：只传一个图片路径时查看图片信息
    if len(sys.argv) == 2:
        get_image_info(sys.argv[1])
    else:
        print('用法: python "second homework.py" <图片路径>')
        print("图片编辑可在代码中调用：")
        print("  resize_image(path, width=None, height=None)")
        print("  crop_image(path, left, top, right, bottom)")
        print("  rotate_image(path, angle)              # 90 / 180 / 270")
        print('  flip_image(path, "horizontal" | "vertical")')
        print("保存结果默认生成新文件，不会覆盖原图。")