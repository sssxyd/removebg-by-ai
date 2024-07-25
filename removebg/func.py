import os
import re
import sys

from pydantic import BaseModel


def get_executable_directory():
    if getattr(sys, 'frozen', False):  # 判断是否为打包后的可执行文件
        executable_path = os.path.realpath(sys.executable)  # 获取实际可执行文件的路径
        directory = os.path.dirname(executable_path)  # 获取实际可执行文件所在的目录
    else:
        directory = os.path.dirname(os.path.realpath(__file__))  # 获取脚本文件所在的目录
        directory = os.path.dirname(directory)
    return directory


class CommandArgs(BaseModel):
    arguments: list[str] = []
    options: set[str] = set()
    parameters: dict[str, str] = dict()


def parse_command() -> CommandArgs:
    dto = CommandArgs()
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if arg.startswith('--'):
            idx = arg.find('=')
            if idx > 0:
                dto.parameters[arg[2:idx].strip()] = arg[idx + 1:].strip()
        elif arg.startswith('-'):
            dto.options.add(arg[1:])
        else:
            dto.arguments.append(arg)
    return dto


def is_http_url(url):
    """
    判断给定的字符串是否是有效的 HTTP 或 HTTPS URL。

    :param url: 待检查的字符串
    :return: 如果字符串是有效的 HTTP 或 HTTPS URL，则返回 True，否则返回 False
    """
    # 正则表达式匹配 HTTP 或 HTTPS URL
    pattern = re.compile(
        r'^https?://'  # http:// 或 https://
        r'([a-zA-Z0-9-]+\.)+'  # 子域名
        r'[a-zA-Z]{2,}'  # 顶级域名
        r'(/\S*)?'  # 可选路径
        r'$'
    )
    return bool(pattern.match(url))


def resolve_path(path):
    """
    判断给定的路径是绝对路径还是相对路径，并将相对路径转换为绝对路径。

    :param path: 待检查的路径字符串
    :return: 绝对路径字符串
    """
    # 判断是否为绝对路径
    if os.path.isabs(path):
        # 如果已经是绝对路径，则直接返回
        return path
    else:
        # 如果是相对路径，则使用 os.getcwd() 获取当前工作目录，并将其与相对路径拼接
        current_dir = os.getcwd()
        absolute_path = os.path.join(current_dir, path)
        return absolute_path
