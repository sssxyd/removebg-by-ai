import io
from PIL import Image
import cv2
import numpy as np

def create_webp_animation_from_cv2(images: list[cv2.Mat], duration=300) -> bytes:
    """
    将 OpenCV 图像列表组合成 WebP 动图。
    
    :param images: 包含 OpenCV 图像 (cv2.Mat) 的列表。
    :param duration: 每帧的间隔时间（毫秒）。
    """
    # 确保有图片
    if not images:
        raise ValueError("未找到符合条件的图片！")

    # 将 OpenCV 图像转换为 Pillow 图像
    frames = [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in images]

    # 使用 BytesIO 保存到内存
    output_buffer = io.BytesIO()
    frames[0].save(
        output_buffer,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,  # 无限循环
        format="WEBP"
    )
    output_buffer.seek(0)  # 重置指针到开头
    return output_buffer.getvalue()  # 返回字节数据

# 示例调用
if __name__ == "__main__":
    # 示例 OpenCV 图像列表
    images = [cv2.imread(f"example/sunshine-{i}.png") for i in range(0, 7)]
    webp_bytes = create_webp_animation_from_cv2(images)
    output_file = "output_animation.webp"
    with open(output_file, "wb") as f:
        f.write(webp_bytes)
    print(f"WebP 动图已保存到: {output_file}")