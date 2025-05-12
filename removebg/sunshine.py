import cv2
import numpy as np

def _find_intersection_points(rect : cv2.typing.Rect, point1: cv2.typing.Point, point2: cv2.typing.Point) -> list[cv2.typing.Point]:
    x, y, w, h = rect
    x1, y1 = point1
    x2, y2 = point2

    # 计算斜率
    if x2 != x1:
        k = (y2 - y1) / (x2 - x1)
    else:
        k = None  # 垂直线

    # 存储交点
    intersection_points = []

    # 与左边界相交 (x = x)
    if k is not None:
        y_left = k * (x - x1) + y1
        if y <= y_left <= y + h:
            intersection_points.append((x, int(y_left)))

    # 与右边界相交 (x = x + w)
    if k is not None:
        y_right = k * (x + w - x1) + y1
        if y <= y_right <= y + h:
            intersection_points.append((x + w, int(y_right)))

    # 与上边界相交 (y = y)
    if k is not None and k != 0:
        x_top = (y - y1) / k + x1
        if x <= x_top <= x + w:
            intersection_points.append((int(x_top), y))

    # 与下边界相交 (y = y + h)
    if k is not None and k != 0:
        x_bottom = (y + h - y1) / k + x1
        if x <= x_bottom <= x + w:
            intersection_points.append((int(x_bottom), y + h))

    # 如果是垂直线
    if k is None:
        if x <= x1 <= x + w:
            intersection_points.append((x1, y))
            intersection_points.append((x1, y + h))

    return intersection_points

def _blend_images(base: cv2.Mat, overlay: cv2.Mat) -> cv2.Mat:
    """
    将两张大小相同的 BGRA 图像合并（叠加）。
    :param base: 底层图像（BGRA 格式）。
    :param overlay: 叠加图像（BGRA 格式）。
    :return: 合并后的图像（BGRA 格式）。
    """
    # 分离 Alpha 通道
    base_rgb = base[:, :, :3]
    base_alpha = base[:, :, 3] / 255.0

    overlay_rgb = overlay[:, :, :3]
    overlay_alpha = overlay[:, :, 3] / 255.0

    # 计算合并后的 Alpha 通道
    out_alpha = overlay_alpha + base_alpha * (1 - overlay_alpha)

    # 防止除以 0 的情况
    out_alpha_safe = np.where(out_alpha == 0, 1, out_alpha)

    # 计算合并后的 RGB 通道
    out_rgb = np.zeros_like(base_rgb, dtype=np.float32)  # 初始化为零
    valid_mask = out_alpha > 0  # 仅处理有效的像素
    out_rgb[valid_mask] = (
        (overlay_rgb[valid_mask] * overlay_alpha[valid_mask, None] +
         base_rgb[valid_mask] * base_alpha[valid_mask, None] * (1 - overlay_alpha[valid_mask, None]))
        / out_alpha_safe[valid_mask, None]
    )

    # 合并 RGB 和 Alpha 通道
    out_image = np.dstack((out_rgb, out_alpha * 255)).astype(np.uint8)

    return out_image

def sunshine(source: cv2.Mat, mask: cv2.Mat, removebg: bool) -> list[cv2.Mat]:
    """
    处理图片的光照效果
    :param source: 原图图片
    :param mask: 原图核心区域的遮罩
    :param removebg: 是否去除原图背景
    :return: 处理后的图片列表
    """
    # 如果 mask 是 (H, W, 1)，去掉最后一个维度
    if mask.shape[-1] == 1:  
        mask = np.squeeze(mask, axis=-1)

    source = cv2.cvtColor(source, cv2.COLOR_BGR2BGRA)
    if removebg:
        # 设置 Alpha 通道：黑色区域 (mask == 0) 设置为透明
        source[:, :, 3] = mask

    rect = cv2.boundingRect(mask)
    x, y, w, h = rect

    # 划分7段需要8个节点
    xstep = w / 8  
    ystep = h / 8

    sunshine_images = []
    for i in range(1, 8):
        # 计算当前分割线位置, 对角线方向
        top_right = (int(x + i * xstep), int(y + (i-1) * ystep))
        bottom_left = (int(x + (i-1) * xstep), int(y + i * ystep))

        rect_point1, rect_point2 = _find_intersection_points(rect, top_right, bottom_left)

        # 创建图像副本
        canvas = source.copy()
        # 创建光照层（带透明度））
        overlay = np.zeros((source.shape[0], source.shape[1], 4), dtype=np.uint8)
    
        # 绘制光照线
        cv2.line(overlay, rect_point1, rect_point2, (255, 255, 255, 255), 25, lineType=cv2.LINE_AA)
        
        # 应用高斯模糊
        overlay = cv2.GaussianBlur(overlay, (51, 51), 0)
        
        # 混合图像（柔和效果）
        blended_image = _blend_images(canvas, overlay)
        blended_image[:, :, 3] = mask 
        sunshine_images.append(blended_image)
    
    return sunshine_images