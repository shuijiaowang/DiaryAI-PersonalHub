from typing import Literal

from pydantic import BaseModel, Field

from app.modules._base import Module
from app.modules.registry import register


class WeatherData(BaseModel):
    天气类型: Literal[
        "晴", "雨", "雪", "阴", "雾霾", "多云", "雨夹雪", "其他"
    ] | None = None
    最低气温: float | None = Field(default=None, description="摄氏度")
    最高气温: float | None = Field(default=None, description="摄氏度")
    其他: dict = Field(default_factory=dict)


@register
class WeatherModule(Module):
    code = "weather"
    name = "天气"
    description = "记录每天的天气状况，方便回顾、关联心情和健康数据。"
    prompt_fragment = (
        "提取日记中提到的天气、气温、路况等。一篇日记最多生成 1 条 weather 事件。"
    )
    DataSchema = WeatherData
