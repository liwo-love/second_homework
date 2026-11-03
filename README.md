# 图片信息查看与编辑工具

基于 **Python + OpenCV** 的图片处理小工具，支持查看图片信息，以及缩放、裁剪、旋转、翻转、灰度化和格式转换等常用操作。

所有编辑操作都会**生成新文件**，不会覆盖原图。

## 功能一览

| 功能 | 函数 | 说明 |
| --- | --- | --- |
| 查看图片信息 | `get_image_info` | 文件名、格式、宽高、颜色模式、文件大小 |
| 缩放 | `resize_image` | 指定宽高，或只给一边按比例缩放 |
| 裁剪 | `crop_image` | 按（左、上、右、下）坐标裁剪 |
| 旋转 | `rotate_image` | 支持 90、180、270 度 |
| 翻转 | `flip_image` | 水平翻转、垂直翻转 |
| 灰度化 | `grayscale_image` | 转为单通道灰度图 |
| 格式转换 | `convert_to_jpg` | PNG 等格式转为 JPG，自动处理透明通道 |
| 交互式菜单 | `interactive_menu` | 在命令行中按提示选择操作 |

## 环境要求

- **Python 3.10**
- **OpenCV**（`opencv-python`，会自动安装 numpy）

## 安装依赖

```bash
pip3 install opencv-python
```

如果系统提示找不到 `pip3`，可以使用：

```bash
python3 -m pip install opencv-python
```

安装完成后验证：

```bash
python3 -c "import cv2; print(cv2.__version__)"
```

能正常输出版本号即可。

## 项目结构

```text
git_text/
├── second homework.py   # 主程序
└── README.md            # 说明文档
```

## 运行方式

进入项目目录：

```bash
cd /home/liwo/Desktop/git_text
```

启动交互式菜单：

```bash
python3 "second homework.py"
```

> 文件名中包含空格，命令里的路径必须加引号。

启动后会看到如下菜单：

```text
========== 图片处理工具 ==========
  1. 查看图片信息
  2. 缩放图片
  3. 裁剪图片
  4. 旋转图片
  5. 翻转图片
  6. 灰度化
  7. 转换为 JPG
  0. 退出
==================================
提示：所有操作都会生成新文件，不会覆盖原图。
```

根据提示输入数字选择操作，再输入图片路径和对应参数即可：

- 缩放时宽度、高度可以只填一个，留空的一边会按比例自动计算（不能两个都留空）
- 裁剪依次输入左、上、右、下坐标
- 翻转输入 `horizontal` / `vertical`，也可以输入 `h` / `v`
- 每次操作完成后按回车返回菜单
- 输入 `0` 退出程序

### 菜单操作示例

以「转换为 JPG」为例：

```text
请选择操作 [0-7]: 7
请输入图片路径: transparent.png
[信息] 检测到透明通道，已先转换为 3 通道 RGB，再保存为 JPG。
[信息] 转换为 JPG：800x600，3 通道
[完成] 已保存：transparent_converted.jpg

按回车返回菜单...
```

以「灰度化」为例：

```text
请选择操作 [0-7]: 6
请输入图片路径: photo.jpg
[信息] 灰度化：1920x1080 -> 单通道灰度图
[完成] 已保存：photo_gray.jpg
```

## 在 Python 中调用

由于文件名包含空格，不能直接 `import`，可以用下面的方式加载模块：

```python
import importlib.util

spec = importlib.util.spec_from_file_location(
    "image_tool", "/home/liwo/Desktop/git_text/second homework.py"
)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
```

以下示例均假设已经通过上面的代码加载为 `tool`。

### 1. 查看图片信息

```python
info = tool.get_image_info("photo.jpg")

if info:
    print(info["width"], info["height"])
    print(info["format"], info["color_mode"], info["file_size"])
```

输出示例：

```text
文件名   : photo.jpg
格式     : JPEG
尺寸     : 1920 x 1080 像素
颜色模式 : RGB
文件大小 : 356.72 KB
```

### 2. 缩放图片

```python
# 只指定宽度：按原图比例计算高度
tool.resize_image("photo.jpg", width=800)

# 只指定高度：按原图比例计算宽度
tool.resize_image("photo.jpg", height=600)

# 同时指定宽高：严格缩放到该尺寸（可能改变宽高比）
tool.resize_image("photo.jpg", width=800, height=600)
```

生成文件示例：

```text
photo_resized_800x450.jpg
photo_resized_1067x600.jpg
photo_resized_800x600.jpg
```

### 3. 裁剪图片

坐标顺序为 **左、上、右、下**，其中右、下为不包含的边界。

```python
# 从 (100, 50) 裁剪到 (500, 400)
tool.crop_image("photo.jpg", left=100, top=50, right=500, bottom=400)
```

生成文件：

```text
photo_cropped_100_50_500_400.jpg
```

如果坐标越界、为负数，或 `left >= right`、`top >= bottom`，程序会给出明确提示并取消操作，不会崩溃。

### 4. 旋转图片

```python
tool.rotate_image("photo.jpg", 90)   # 顺时针 90 度
tool.rotate_image("photo.jpg", 180)  # 旋转 180 度
tool.rotate_image("photo.jpg", 270)  # 逆时针 90 度（顺时针 270 度）
```

生成文件：

```text
photo_rotated_90.jpg
photo_rotated_180.jpg
photo_rotated_270.jpg
```

旋转 90 或 270 度后，图片的宽高会自动交换。

### 5. 翻转图片

```python
# 水平翻转（左右镜像）
tool.flip_image("photo.jpg", "horizontal")

# 垂直翻转（上下翻转）
tool.flip_image("photo.jpg", "vertical")
```

也支持简写和中文参数：

```python
tool.flip_image("photo.jpg", "h")
tool.flip_image("photo.jpg", "v")
tool.flip_image("photo.jpg", "水平")
tool.flip_image("photo.jpg", "垂直")
```

生成文件：

```text
photo_flipped_h.jpg
photo_flipped_v.jpg
```

### 6. 灰度化

```python
tool.grayscale_image("photo.jpg")
tool.grayscale_image("transparent.png")  # 带透明通道也可以处理
```

生成文件：

```text
photo_gray.jpg
transparent_gray.png
```

带透明通道的图片灰度化时会丢弃 alpha 通道，输出单通道灰度图。

### 7. 转换为 JPG

```python
# 普通 PNG -> JPG
tool.convert_to_jpg("photo.png")

# 带透明通道的 RGBA PNG -> JPG
tool.convert_to_jpg("transparent.png")

# 自定义输出路径（扩展名必须是 .jpg 或 .jpeg）
tool.convert_to_jpg("photo.png", output_path="result.jpg")
```

生成文件：

```text
photo_converted.jpg
transparent_converted.jpg
```

**透明通道处理说明：**

JPEG 不支持 alpha 通道，带透明通道的 PNG 如果直接保存为 JPG 会出错。程序会先执行：

```python
image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
```

把 4 通道 BGRA 转成 3 通道 BGR 后再保存，因此不会报错。

## 输出规则

- 默认在原图旁边生成新文件，原图保持不变
- 目标文件已存在时自动加序号，例如 `photo_resized_800x450_1.jpg`
- 输出路径如果与原图相同，程序会拒绝保存
- 编辑 PNG 时，缩放、裁剪、旋转、翻转会保留透明通道；灰度化会丢弃 alpha；输出为 JPG 时透明通道会丢失
- 除 `get_image_info` 返回信息字典外，编辑函数成功时返回保存路径，失败时返回 `None`

各操作的默认文件后缀：

| 操作 | 后缀示例 |
| --- | --- |
| 缩放 | `_resized_800x450` |
| 裁剪 | `_cropped_100_50_500_400` |
| 旋转 | `_rotated_90` |
| 水平翻转 | `_flipped_h` |
| 垂直翻转 | `_flipped_v` |
| 灰度化 | `_gray` |
| 转 JPG | `_converted.jpg` |

## 注意事项

1. **文件名含空格**：运行和调用时，路径要加引号，例如 `python3 "second homework.py"`。
2. **颜色模式**：OpenCV 内部使用 BGR/BGRA，程序展示时按用户习惯称为 RGB/RGBA。
3. **旋转方向**：90 度为顺时针，270 度为逆时针。
4. **JPG 与透明通道**：JPG 不支持 alpha，转 JPG 时会自动丢弃透明通道。
5. **异常处理**：文件不存在、空文件、不是有效图片、坐标越界、参数非法等情况都会给出提示，不会导致程序崩溃。
