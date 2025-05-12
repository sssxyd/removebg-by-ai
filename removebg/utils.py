
import base64
import os
import cv2
import numpy as np
import requests
from .logger import get_logger
from .func import get_executable_directory, is_http_url

def read_image_to_mat(path_or_url: str, base64_data: str) -> cv2.Mat:
    """
    读取图片到 OpenCV Mat 对象
    :param dto: RemoveBgDTO 对象
    :return: OpenCV Mat 对象
    """
    log = get_logger("removebg")
    try:
        if is_http_url(path_or_url):
            response = requests.get(path_or_url)
            if response.status_code != 200:
                log.error(f"get image from {path_or_url} failed")
                return None
            image_data = response.content
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_UNCHANGED)
            if image is None:
                log.error(f"decode image from {path_or_url} failed")
                return None
            return image
        elif path_or_url:
            image_path = path_or_url if os.path.isabs(path_or_url) else os.path.join(get_executable_directory(), path_or_url)
            if not os.path.exists(image_path) or not os.path.isfile(image_path):
                log.error(f"path: {path_or_url} not exist or it is not file!")
                return None
            # 读取图片
            image = cv2.imread(path_or_url)
            if image is None:
                log.error(f"read image from {path_or_url} failed")
                return None
            return image
        elif base64_data:
            base64_string = base64_data
            if ";base64," in base64_string:
                base64_string = base64_string.split(";base64,")[-1]
            image_data = base64.b64decode(base64_string)
            image_array = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
            if image is None:
                log.error(f"decode image from base64 failed")
                return None
            return image
        else:
            log.error("path, url, base64 all not set")
            return None
    except Exception as e:
        log.exception(msg="read_image_to_mat failed", exc_info=e)
        return None
    
def crop_image_polygon_area(image: cv2.Mat, polygon_points: list[tuple[float, float]], canvas_size: tuple[float, float]) -> cv2.Mat:
    """
    使用 OpenCV 实现裁剪多边形区域的功能。

    :param image: 输入图像 (cv2.Mat)。
    :param polygon_points: 多边形的点列表 [(x1, y1), (x2, y2), ...]。
    :param canvas_size: 画布大小 (width, height)。
    :return: 裁剪后的图像 (cv2.Mat)。
    """
    if len(polygon_points) < 3:
        return image

    # 获取图像宽高
    image_height, image_width = image.shape[:2]
    canvas_width, canvas_height = canvas_size

    # 计算缩放比例
    width_factor = 1 if canvas_width <= 0 else image_width / canvas_width
    height_factor = 1 if canvas_height <= 0 else image_height / canvas_height

    # 计算真实的多边形点坐标
    real_points = []
    for point_x, point_y in polygon_points:
        point_x = point_x * width_factor
        point_y = point_y * height_factor
        point_x = max(0, min(point_x, image_width))
        point_y = max(0, min(point_y, image_height))
        real_points.append((int(point_x), int(point_y)))

    # 创建一个与原图大小相同的透明 mask
    mask = np.zeros((image_height, image_width), dtype=np.uint8)
    cv2.fillPoly(mask, [np.array(real_points, dtype=np.int32)], 255)

    # 将原图与 mask 合并，使未选中部分透明
    image_with_alpha = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
    image_with_alpha[:, :, 3] = mask

    # 计算多边形的边界框
    x, y, w, h = cv2.boundingRect(np.array(real_points, dtype=np.int32))

    # 根据边界框裁剪图像
    cropped_image = image_with_alpha[y:y+h, x:x+w]

    return cropped_image