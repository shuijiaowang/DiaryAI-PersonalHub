from typing import Literal

from pydantic import BaseModel, Field

from app.modules._base import Module
from app.modules.registry import register


class ExpenseData(BaseModel):
    消费类型: Literal[
        "日常", "饮食", "出行", "购物", "住房", "娱乐", "学习", "医疗", "其他"
    ] = "其他"
    平台: str = ""
    店铺: str = ""
    评价: str = ""
    价格: float = Field(description="单位：元")
    其他: dict = Field(default_factory=dict)


@register
class ExpenseModule(Module):
    code = "expense"
    name = "消费"
    description = "提取一切花钱的事件，用于做日/月/年支出统计。"
    prompt_fragment = (
        "提取所有支付行为，包括饮食、出行、租金、订阅等。"
        "饮食类的消费可以同时生成 meal 和 expense 两条事件（不同视角）。"
        "押金 + 租金这种合计支付的情况，价格填总额，明细放进 `其他`。"
    )
    DataSchema = ExpenseData
