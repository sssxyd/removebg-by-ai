# RemoveBG by AI

[![GitHub stars](https://img.shields.io/github/stars/sssxyd/removebg-by-ai)](https://github.com/sssxyd/removebg-by-ai/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/sssxyd/removebg-by-ai)](https://github.com/sssxyd/removebg-by-ai/issues)
[![GitHub license](https://img.shields.io/github/license/sssxyd/removebg-by-ai)](https://github.com/sssxyd/removebg-by-ai/blob/main/LICENSE)

## 项目简介

RemoveBG by AI 是一个利用AI模型对指定图片的指定矩形区域进行抠图，将该区域内的主要单一物体或人物扣取出来，去除背景的工具。该项目使用了 [RMBG-1.4 AI模型](https://huggingface.co/briaai/RMBG-1.4)。

## 效果展示
<p align="center">
    <img src="example/1-上传图片.jpg" alt="上传图片" width="30%">
    <img src="example/2-鼠标框选.jpg" alt="框选区域" width="30%">
    <img src="example/3-抠图下载.jpg" alt="抠图效果" width="30%">
</p>

## 功能特性

- 自动识别并抠取指定区域内的主要物体/人物
- 去除背景，使物体/人物更加突出
- 不依赖显卡，可在普通办公电脑上运行
- 提供简单易用的API接口

## 安装与使用

### Windows用户

1. 从[发布页面](https://github.com/sssxyd/removebg-by-ai/releases)下载最新的zip文件。
2. 解压文件。
3. 运行程序。
4. 访问：http://localhost

端口号默认80，如需修改端，可编辑 `.env` 文件。

### 源码编译

1. 确保 Python 版本 >= 3.10。
2. 安装 Git LFS：

    ```sh
    git lfs install
    ```

3. 克隆此仓库并下载大文件：

    ```sh
    git clone https://github.com/sssxyd/removebg-by-ai.git
    cd removebg-by-ai
    git lfs pull
    ```

4. 创建虚拟环境并安装依赖：

    ```sh
    python -m venv venv
    source venv/bin/activate  # Windows 用户使用 `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

5. 运行程序：

    ```sh
    python start.py
    ```

## API接口

### /removebg

- **Method**: POST
- **Content-Type**: application/json
- **Parameters**:
  - `path: str` - 图片的相对地址；path/url/base64三选一
  - `url: str` - 图片的http地址；path/url/base64三选一
  - `base64: str` - 图片的base64格式数据；path/url/base64三选一
  - `selectPolygon: [[x1,y1], [x2, y2], [x3, y3], [x4, y4]]` - 可选，图片上的rectangle四个点的坐标
  - `editorSize: [width, height]` - 可选，框选图片时，图片缩放图的宽度和高度
  - `responseFormat: int = 0` - 返回的数据类型 0/1, 默认0
- **Return**:
  - responseFormat == 0: application/json {code:int, msg:string, result:base64Str}， code == 0 则成功，否则失败
  - responseFormat == 1: image/png字节流
 
### /removebg

- **Method**: GET
- **Parameters**:
  - `url: str` - 图片的http地址
- **Return**:
  - 成功: image/png字节流
  - 失败: application/json {code:int, msg:string} 
  
## 使用示例

```python
import requests

url = 'http://localhost:5000/removebg'
data = {
    'url': 'https://website.com/example.jpg',
    'selectPolygon': [(10, 10), (10, 100), (100, 100), (100, 10)],
    'responseFormat': 1
}

response = requests.post(url, json=data)
if response.headers['Content-Type'] == 'application/json':
    result = response.json()
else:
    with open('output.png', 'wb') as f:
        f.write(response.content)
