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


if __name__ == "__main__":
    # 简单演示：命令行传入图片路径即可
    import sys

    if len(sys.argv) != 2:
        print("用法: python image_info.py <图片路径>")
    else:
        get_image_info(sys.argv[1])
