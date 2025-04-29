import logging
import os
from huggingface_hub import snapshot_download
import requests

from removebg import get_logger

def is_china_ip() -> bool:
    log = get_logger("download_model")
    try:
        # 查询当前 IP 的地理位置
        response = requests.get("http://ip-api.com/json/")
        data = dict(response.json())

        if data.get("status") != 'success':
            log.warning("Unable to determine IP location")
            return False
        
        log.info(f"IP {data.get('query')} location: {data.get('country')}")
        
        # 检查国家是否为中国
        if data.get("country") == "China":
            return True
        return False
    except Exception as e:
        log.warning(f"Unable to determine which country this IP belongs to: {e}")
        return False
    
def download_model():
    log = get_logger("download_model")
    # 定义目标目录
    local_dir = "model/ZhengPeng7/BiRefNet"

    # 确保目标目录存在
    os.makedirs(local_dir, exist_ok=True)

    # 下载模型到本地 model 目录下的子文件夹
    if is_china_ip():
        # 如果是中国 IP，则设置国内镜像地址
        log.info("Using domestic mirror [https://hf-mirror.com] for model download")
        # os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        endpoint_url = "https://hf-mirror.com"
    else:
        # 否则使用默认的 Hugging Face 地址
        # os.environ.pop("HF_ENDPOINT", None)  # 确保没有设置自定义镜像
        endpoint_url = "https://huggingface.co"

    # log.info(f">>>{os.environ["HF_ENDPOINT"]}")
    # 调用 snapshot_download 下载模型
    snapshot_download(
        repo_id="ZhengPeng7/BiRefNet",
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        endpoint=endpoint_url,
    )
    log.info("Model downloaded successfully")


if __name__ == "__main__":
    user_home = os.path.expanduser("~")
    print(user_home)
    # download_model()