"""NLU 请求和响应数据模型"""

from pydantic import BaseModel
from typing import Dict, List


class TextInput(BaseModel):
    """请求输入模型"""
    text: str


class IntentResult(BaseModel):
    """意图识别结果"""
    name: str
    confidence: float


class EntityResult(BaseModel):
    """实体提取结果"""
    entity: str
    value: str
    start: int
    end: int
    confidence: float


class NLUResponse(BaseModel):
    """NLU 响应模型"""
    text: str
    intent: IntentResult
    entities: List[EntityResult] = []
    intent_ranking: List[Dict] = []
