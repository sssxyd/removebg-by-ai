import os.path
from urllib.parse import urlparse

from pydantic import BaseModel

from .logger import get_logger


class RemoveBgDTO(BaseModel):
    path: str = ''
    url: str = ''
    base64: str = ''
    selectPolygon: list[tuple[float, float]] = []
    editorSize: tuple[float, float] = (0, 0)
    responseFormat: int = 0  # 0: base64 1: image/png

    def check(self) -> tuple[int, str]:
        if not self.path and not self.url and not self.base64:
            return 100, 'One of the path/url/base64 parameters must have a value'
        if self.path:
            absolute_path = os.path.join(os.getcwd(), self.path)
            if not os.path.exists(absolute_path) or not os.path.isfile(absolute_path):
                return 110, f"path: {self.path} not exist or it is not file!"
        elif self.url:
            try:
                urlparse(self.url)
            except Exception as e:
                get_logger('removebg').exception(msg="RemoveBgDTO check failed", exc_info=e)
                return 120, f"url: {self.url} is not valid url!"
        return 0, "OK"

