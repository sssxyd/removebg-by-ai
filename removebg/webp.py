from PIL import Image
import cv2
import numpy as np

def create_webp_animation_from_cv2(images: list[cv2.Mat], output_path: str, duration=300):
    """
    将 OpenCV 图像列表组合成 WebP 动图。
    
    :param images: 包含 OpenCV 图像 (cv2.Mat) 的列表。
    :param output_path: 输出 WebP 动图的路径。
    :param duration: 每帧的间隔时间（毫秒）。
    """
    # 确保有图片
    if not images:
        raise ValueError("未找到符合条件的图片！")

    # 将 OpenCV 图像转换为 Pillow 图像
    frames = [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in images]

    # 保存为 WebP 动图
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,  # 无限循环
        format="WEBP"
    )
    print(f"WebP 动图已保存到: {output_path}")

# 示例调用
if __name__ == "__main__":
    # 示例 OpenCV 图像列表
    images = [cv2.imread(f"example/sunshine-{i}.png") for i in range(0, 7)]
    output_file = "output_animation.webp"
    create_webp_animation_from_cv2(images, output_file)