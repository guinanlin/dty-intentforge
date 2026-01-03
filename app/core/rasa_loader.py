"""Rasa NLU 模型加载器（单例模式）"""

import os
from app.core.config import settings

# Rasa 3.6.x 使用 Agent 来加载模型，通过 agent.parse_message() 异步方法解析文本
try:
    from rasa.model import get_latest_model
    from rasa.core.agent import Agent
    HAS_AGENT = True
except ImportError:
    HAS_AGENT = False
    Agent = None


class RasaNLULoader:
    """Rasa NLU 模型加载器，使用单例模式确保模型只加载一次"""
    
    _agent = None  # Agent 实例
    
    @classmethod
    def get_agent(cls):
        """
        获取 Rasa Agent（单例）
        
        在 Rasa 3.6.x 中，通过 Agent 加载模型，使用 agent.parse_message() 异步方法解析文本
        
        Returns:
            Agent: Rasa Agent 实例
            
        Raises:
            FileNotFoundError: 模型文件不存在
            ImportError: 无法导入 Rasa Agent
        """
        if cls._agent is None:
            if not os.path.exists(settings.MODEL_PATH):
                raise FileNotFoundError(
                    f"模型文件不存在: {settings.MODEL_PATH}\n"
                    "请先运行训练脚本: python scripts/train_rasa_nlu.py"
                )
            
            if not HAS_AGENT or Agent is None:
                raise ImportError(
                    "无法导入 Rasa Agent。\n"
                    "请确保已正确安装 Rasa 3.6.x 版本。"
                )
            
            # 使用 Agent 加载模型
            print(f"加载 Rasa 模型: {settings.MODEL_PATH}")
            cls._agent = Agent.load(settings.MODEL_PATH)
        
        return cls._agent


# 导出便捷函数
agent = RasaNLULoader.get_agent
