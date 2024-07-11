import base64
import os
from io import BytesIO

import requests
from transformers import AutoModelForImageSegmentation
from torchvision.transforms.functional import normalize

import numpy as np
import torch
import torch.nn.functional as F
import skimage.io as io
from PIL import Image, ImageDraw
from .logger import get_logger
from .dto import RemoveBgDTO

model = AutoModelForImageSegmentation.from_pretrained(os.path.join(os.getcwd(), 'model', 'briaai', 'RMBG-1.4'),
                                                      trust_remote_code=True)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model.to(device)


def _read_image(dto: RemoveBgDTO) -> Image.Image | str:
    msg = ""
    try:
        if dto.path:
            image_path = os.path.join(os.getcwd(), dto.path)
            msg = f"read image from {image_path} failed"
            return Image.open(fp=image_path, mode='r')
        elif dto.url:
            response = requests.get(dto.url)
            msg = f"get image from {dto.url} failed"
            return Image.open(BytesIO(response.content))
        else:
            base64_string = dto.base64
            msg = f"parse base64 image failed"
            if ";base64," in base64_string:
                base64_string = base64_string.split(";base64,")[-1]
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
    except Exception as e:
        get_logger("removebg").exception("get image failed", exc_info=e)
        return msg


def _crop_image_polygon_area(dto: RemoveBgDTO, image: Image.Image) -> Image.Image:
    if len(dto.selectPolygon) < 3:
        return image
    # 根据缩放比例计算真实的多边形点的坐标
    image_width, image_height = image.size
    editor_width, editor_height = dto.editorSize
    width_factor = 1 if editor_width <= 0 else image_width / editor_width
    height_factor = 1 if editor_height <= 0 else image_height / editor_height
    real_points = []
    for item in dto.selectPolygon:
        point_x, point_y = item
        point_x = point_x * width_factor
        point_y = point_y * height_factor
        if point_x < 0:
            point_x = 0
        elif point_x > image_width:
            point_x = image_width

        if point_y < 0:
            point_y = 0
        elif point_y > image_height:
            point_y = image_height

        real_points.append((point_x, point_y))

    # 创建一个和原图一样大小的透明mask
    mask = Image.new("L", image.size, 0)
    # 使用ImageDraw在mask上绘制多边形，255表示完全不透明
    ImageDraw.Draw(mask).polygon(real_points, outline=255, fill=255)
    # 将mask转换为透明度通道，其中0表示完全透明，255表示完全不透明
    image.putalpha(mask)
    # 使用mask来剪裁多边形区域
    # 计算多边形的边界框
    x_min, y_min, x_max, y_max = mask.getbbox()
    # 根据边界框裁剪图像
    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    return cropped_image


def _preprocess_image(im: np.ndarray, model_input_size: list) -> torch.Tensor:
    if len(im.shape) < 3:
        im = im[:, :, np.newaxis]
    # orig_im_size=im.shape[0:2]
    im_tensor = torch.tensor(im, dtype=torch.float32).permute(2, 0, 1)
    im_tensor = F.interpolate(torch.unsqueeze(im_tensor, 0), size=model_input_size, mode='bilinear')
    image = torch.divide(im_tensor, 255.0)
    image = normalize(image, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    return image


def _post_process_image(tensor_ret: torch.Tensor, im_size: list) -> np.ndarray:
    tensor_ret = torch.squeeze(F.interpolate(tensor_ret, size=im_size, mode='bilinear'), 0)
    ma = torch.max(tensor_ret)
    mi = torch.min(tensor_ret)
    tensor_ret = (tensor_ret - mi) / (ma - mi)
    im_array = (tensor_ret * 255).permute(1, 2, 0).cpu().data.numpy().astype(np.uint8)
    im_array = np.squeeze(im_array)
    return im_array


def _remove_background(input_image: Image.Image) -> Image:
    image_array = np.array(input_image)
    orig_im_size = image_array.shape[0:2]
    image = _preprocess_image(image_array, [1024, 1024]).to(device)

    # inference
    result = model(image)  # tuple 2*6

    # post process
    result_image = _post_process_image(result[0][0], list(orig_im_size))

    # save result
    return Image.fromarray(result_image)


def _save_as_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_byte = buffered.getvalue()
    img_base64 = base64.b64encode(img_byte)
    # Python 3.x 中 base64.b64encode() 返回的是 bytes，如果需要字符串形式，需要解码
    img_base64_str = img_base64.decode('utf-8')
    return img_base64_str


def _save_as_bytes(image: Image.Image) -> bytes:
    # 将图像保存到字节流
    img_byte_array = BytesIO()
    image.save(img_byte_array, format='PNG')
    img_byte_array = img_byte_array.getvalue()
    return img_byte_array


def process(dto: RemoveBgDTO) -> (int, str, bytes | str):
    code, msg = dto.check()
    if code != 0:
        return code, msg, ''

    orig_im: Image | str = _read_image(dto)
    if isinstance(orig_im, str):
        return 200, orig_im, ''
    crop_im = _crop_image_polygon_area(dto, orig_im)
    result = _remove_background(crop_im)
    if dto.responseFormat == 0:
        return 0, '', _save_as_base64(result)
    else:
        return 0, '', _save_as_bytes(result)
