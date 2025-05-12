
import os
import time
import cv2
import numpy as np
import torch.nn.functional as F
import torch
from .func import get_executable_directory
from transformers import AutoModelForImageSegmentation

def _load_model() -> AutoModelForImageSegmentation:
    """加载模型
    :return: 加载的模型
    """
    root_dir = get_executable_directory()
    model_dir = os.path.join(root_dir, 'model', 'briaai', 'RMBG-1.4')
    model = AutoModelForImageSegmentation.from_pretrained(model_dir, trust_remote_code=True)
    model.to("cpu")
    model.eval()
    return model

def _images_to_tensor(input_images: list[np.ndarray], model_input_size: list) -> tuple[torch.Tensor, list[tuple]]:
    """
    将输入图像列表转换为模型输入张量

    :param input_images: 输入图像列表
    :param model_input_size: 模型输入大小
    :return: 转换后的张量和每张图片的原始大小列表
    """
    tensors = []
    original_sizes = []

    for input_image in input_images:
        # 记录原始大小 (height, width)
        original_sizes.append((input_image.shape[0], input_image.shape[1]))

        # 如果输入图像是单通道灰度图像，则将其转换为三通道RGB图像
        if len(input_image.shape) < 3:
            input_image = cv2.cvtColor(input_image, cv2.COLOR_GRAY2BGR)
        elif input_image.shape[2] == 4:  # 如果有 alpha 通道
            input_image = cv2.cvtColor(input_image, cv2.COLOR_BGRA2BGR)
        elif input_image.shape[2] == 3:  # 如果是 BGR 格式
            input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        
        # (height, width, channels) => (channels, height, width)
        input_tensor = torch.tensor(input_image, dtype=torch.float32).permute(2, 0, 1)
        
        # 调整尺寸到模型输入大小
        input_tensor = F.interpolate(torch.unsqueeze(input_tensor, 0), size=model_input_size, mode='bilinear')
        
        # 归一化到 [0, 1]
        input_tensor = torch.divide(input_tensor, 255.0)
        
        tensors.append(input_tensor)
    
    # 将所有张量沿批次纬度堆叠为一个四维张量 (batch_size, channels, height, width)
    batch_tensor = torch.cat(tensors, dim=0)
    return batch_tensor, original_sizes

def _tensor_to_images(output_tensor: torch.Tensor, original_sizes: list[tuple]) -> list[cv2.Mat]:
    """
    将模型推理的输出张量解析为多张图片。

    :param output_tensor: 模型推理后的输出张量，形状为 (batch_size, channels, height, width)。
    :param original_sizes: 每张图片的原始尺寸列表 [(height1, width1), (height2, width2), ...]。
    :return: 解析后的图片列表，每张图片为 NumPy 数组。
    """
    images = []
    batch_size = output_tensor.shape[0]

    for i in range(batch_size):
        # 提取当前图片的张量
        single_tensor = output_tensor[i]  # 形状为 (channels, height, width)
        
        # 获取对应的原始尺寸
        original_size = original_sizes[i]

        
        # 调整尺寸到原始大小
        resized_tensor = F.interpolate(single_tensor.unsqueeze(0), size=original_size, mode='bilinear')
        
        # 去掉批次维度并归一化到 [0, 1]
        resized_tensor = torch.squeeze(resized_tensor, 0)
        ma = torch.max(resized_tensor)
        mi = torch.min(resized_tensor)
        normalized_tensor = (resized_tensor - mi) / (ma - mi)
        
        # 转换为 NumPy 数组并调整为 (height, width, channels)
        image_array = (normalized_tensor * 255).permute(1, 2, 0).cpu().data.numpy().astype(np.uint8)
        
        # 添加到结果列表
        images.append(image_array)
    return images  

def _extract_max_area_connected_component(input_mask: cv2.Mat) -> cv2.Mat:
    """
    将输入的mask中除了最大的目标区域外的其他区域置为0
    :param input_mask: 输入的mask，形状为 (H, W, 1)
    :return: 处理后的mask，保留最大连续区域
    """
    # 查找所有连通域
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(input_mask, connectivity=8)

    # 如果没有连通域，直接返回全零的mask
    if num_labels <= 1:
        return np.zeros_like(input_mask, dtype=np.uint8)
    
    if num_labels == 2:
        # 只有一个连通域（背景和前景），直接返回前景
        return input_mask

    # 找到面积最大的连通域（排除背景，背景的label为0）
    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])

    # 创建一个新的mask，仅保留最大连通域
    output_mask = np.zeros_like(input_mask, dtype=np.uint8)
    output_mask[labels == largest_label] = 255

    return output_mask

class BackGroundMaskSeparator:
    """
    背景遮罩分离器
    """
    def __init__(self):
        self.model = _load_model()

    # 将图片的背景去除
    def calc_mask(self, input_images: list[cv2.Mat]) -> list[cv2.Mat]:
        start_time = time.time()
        input_tensor, image_size = _images_to_tensor(input_images, [1024, 1024])
        # 进行推理
        results = self.model(input_tensor)
        output_tensor = results[0][0]
        # 解析输出张量为图片
        masks = _tensor_to_images(output_tensor, image_size)
        results = []
        for mask in masks:
            results.append(_extract_max_area_connected_component(mask))
        end_time = time.time()
        print(f"calc_mask time: {end_time - start_time:.2f} seconds")
        return results
    
    