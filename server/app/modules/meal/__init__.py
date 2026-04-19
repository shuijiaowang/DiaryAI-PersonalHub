from typing import Literal

from pydantic import BaseModel, Field

from app.modules._base import Module
from app.modules.registry import register


class MealData(BaseModel):
    时间: Literal["早餐", "午餐", "晚餐", "宵夜", "零食", "其他"] = "其他"
    饭菜: str = ""
    平台: str = ""
    店铺: str = ""
    评价: str = ""
    价格: float | None = Field(default=None, description="单位：元")
    其他: dict = Field(default_factory=dict)


@register
class MealModule(Module):
    code = "meal"
    name = "饮食"
    description = "解析饮食事件，统计花费、营养、外卖频率等。"
    prompt_fragment = (
        "把每一餐拆成独立的 meal 事件（早餐/午餐/晚餐/宵夜/零食）。"
        "如果同一餐里既有付费的外卖、又有自制的食物，应拆为两条独立条目。"
    )
    DataSchema = MealData
