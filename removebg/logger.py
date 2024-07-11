import logging
import os
from enum import Enum


class LogLevel(Enum):
    FATAL = 50
    ERROR = 40
    WARN = 30
    INFO = 20
    DEBUG = 10
    UNSET = 0


global_log_level: LogLevel = LogLevel.INFO


def set_global_log_level(level: LogLevel):
    global global_log_level
    global_log_level = level


def get_log_level(level: str) -> int:
    level = level.strip().upper()
    if level == "FATAL" or level == "CRITICAL":
        return LogLevel.FATAL.value
    if level == "ERROR":
        return LogLevel.ERROR.value
    if level == "WARN" or level == "WARNING":
        return LogLevel.WARN.value
    if level == "INFO":
        return LogLevel.INFO.value
    if level == "DEBUG":
        return LogLevel.DEBUG.value
    return global_log_level.value


def get_logger(name: str, level: LogLevel = LogLevel.UNSET, file_name: str = 'app') -> logging.Logger:
    log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_file_path = os.path.join(log_dir, f"{file_name}.log")
    log = logging.getLogger(name)

    log_level = global_log_level if level == LogLevel.UNSET else level
    formatter = logging.Formatter('%(asctime)s - %(name)s:%(filename)s:%(lineno)d[%(levelname)s] - %(message)s')

    if not log.handlers:  # Avoid adding duplicate handlers
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        log.addHandler(console_handler)

        info_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        info_handler.setLevel(logging.DEBUG)
        info_handler.setFormatter(formatter)
        log.addHandler(info_handler)

    log.setLevel(log_level.value)  # 设置日志记录器级别
    return log
