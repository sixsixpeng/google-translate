# -*- coding: UTF-8 -*-
# 2026/4/16 17:35
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


@dataclass
class p_task:
    func: str
    args: set = field(default_factory=set)
    kwargs: dict = field(default_factory=dict)

    def __repr__(self):
        return {"func": f"{self.func}", "args": f"{self.args}", "kwargs": f"{self.kwargs}"}


class LocatorType(Enum):
    """定位方式枚举"""
    ID = "id"
    CSS = "css selector"
    XPATH = "xpath"
    TEXT = "text"


@dataclass  # frozen=True 使对象不可变，防止意外修改
class selector:
    """
    元素定位符数据类

    Attributes:
        name: 元素名称（用于日志和调试）
        locator_type: 定位方式（ID/CSS/XPATH等）
        value: 定位表达式的值
        description: 可选的元素描述
    """
    name: str
    locator_type: LocatorType
    value: str
    description: Optional[str] = None  # 可选字段，默认为 None

    def __repr__(self):
        """用于调试的字符串表示"""
        desc = f" - {self.description}" if self.description else ""
        return f"[{self.name}] {self.locator_type.value}='{self.value}'{desc}"

    def __str__(self):
        """用于调试的字符串表示"""
        desc = f" - {self.description}" if self.description else ""
        return f"[{self.name}] {self.locator_type.value}='{self.value}'{desc}"

    def __call__(self):
        return f"{self.locator_type.value}={self.value}"


class ele_selector(str, Enum):
    char_btn = selector("文字按钮", LocatorType.XPATH, '(//button//div[@class="VfPpkd-RLmnJb"])[4]')()
    claer_char_btn = selector("文字清空按钮", LocatorType.XPATH, '(//div[@jsname="s3Eaab"])[15]')()
    input_char_btn = selector("文字输入框", LocatorType.XPATH, '//textarea')()

    img_btn = selector("图片按钮", LocatorType.XPATH, '(//button//div[@class="VfPpkd-RLmnJb"])[5]')()
    claer_img_btn = selector("图片清空按钮", LocatorType.XPATH, '(//div[@jsname="s3Eaab"])[15]')()
