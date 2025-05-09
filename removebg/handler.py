
import os
import cv2
import numpy as np
from regex import F
import torch
from removebg.func import get_executable_directory
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
        
        # 如果是单通道图像，去掉多余的维度
        image_array = np.squeeze(image_array)

        # 转换为 BGRA 格式
        if image_array.shape[-1] == 3:  # 如果是 RGB 格式
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGRA)
        elif image_array.shape[-1] == 1:  # 如果是灰度图
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGRA)
        
        # 设置 Alpha 通道：假设模型输出的背景部分为 0，前景部分为 1
        alpha_channel = normalized_tensor[0].cpu().data.numpy() * 255  # 使用第一个通道作为 Alpha 通道
        alpha_channel = alpha_channel.astype(np.uint8)
        image_array[:, :, 3] = alpha_channel  # 替换 Alpha 通道        
        
        # 添加到结果列表
        images.append(image_array)
    return images  

class ImageHandler:
    def __init__(self):
        self.model = _load_model()
    
    def _tensor_to_image(self, tensor_ret: torch.Tensor, im_size: list) -> np.ndarray:
        tensor_ret = torch.squeeze(F.interpolate(tensor_ret, size=im_size, mode='bilinear'), 0)
        ma = torch.max(tensor_ret)
        mi = torch.min(tensor_ret)
        tensor_ret = (tensor_ret - mi) / (ma - mi)
        im_array = (tensor_ret * 255).permute(1, 2, 0).cpu().data.numpy().astype(np.uint8)
        im_array = np.squeeze(im_array)
        return im_array    

    # 将图片的背景去除
    def remove_background(self, input_images: list[cv2.Mat]) -> list[cv2.Mat]:
        input_tensor, image_size = _images_to_tensor([input_images], [1024, 1024])
        # 进行推理
        output_tensor = self.model(input_tensor)
        # 解析输出张量为图片
        return _tensor_to_images(output_tensor, image_size)
    
    # 对source图片中的target目标区域，添加光照效果
    def light_sweeps_past(self, source: cv2.Mat, target: cv2.Mat) -> cv2.Mat:
        return source
    