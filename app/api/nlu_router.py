"""意图识别 API 路由"""

import logging
from fastapi import APIRouter, HTTPException
from app.schemas.nlu_schema import TextInput, NLUResponse, IntentResult, EntityResult
from app.core.rasa_loader import RasaNLULoader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/nlu", tags=["NLU"])


@router.post("/predict", response_model=NLUResponse)
async def predict_intent(input: TextInput):
    """
    意图识别接口
    
    接收用户输入的自然语言文本，识别用户的意图和提取关键实体。
    无论输入什么内容，都会返回一个意图（明确意图或通用意图）。
    
    Args:
        input: 包含文本输入的请求体
        
    Returns:
        NLUResponse: 包含意图、实体和意图排名的响应
        
    Raises:
        HTTPException: 输入文本为空或模型未加载
    """
    logger.info(f"收到意图识别请求: {input.text[:50]}...")
    
    # 1. 输入验证
    if not input.text.strip():
        raise HTTPException(status_code=400, detail="输入文本不能为空")
    
    # 2. 获取 Rasa Agent
    try:
        logger.info("正在获取 Rasa Agent...")
        agent = RasaNLULoader.get_agent()
        logger.info("Rasa Agent 获取成功")
    except (FileNotFoundError, ImportError) as e:
        logger.error(f"获取 Rasa Agent 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取 Rasa Agent 时发生未知错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取模型失败: {str(e)}")
    
    # 3. 调用模型进行推理（异步方法）
    # 注意：无论输入什么，Rasa 模型都会返回一个意图
    # - 如果能匹配到明确意图（置信度 ≥ 0.3），返回明确意图
    # - 如果无法匹配到明确意图（所有明确意图置信度 < 0.3），返回 nlu_fallback
    try:
        logger.info(f"开始调用 agent.parse_message()...")
        result = await agent.parse_message(input.text)
        logger.info(f"模型解析完成，结果类型: {type(result)}")
        logger.info(f"结果内容: {result}")
    except Exception as e:
        logger.error(f"模型解析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"模型解析失败: {str(e)}"
        )
    
    # 4. 格式化返回结果
    # Rasa 3.6.x 的 parse_message 返回格式可能是 Message 对象或字典
    try:
        logger.info("开始格式化返回结果...")
        
        # 处理不同的返回格式
        logger.info(f"结果类型: {type(result)}")
        logger.info(f"结果内容: {result}")
        
        if hasattr(result, 'as_dict'):
            # 如果是 Message 对象，转换为字典
            logger.info("检测到 Message 对象，调用 as_dict()...")
            result_dict = result.as_dict()
        elif isinstance(result, dict):
            logger.info("检测到字典类型")
            result_dict = result
        else:
            # 尝试直接访问属性
            logger.info("尝试直接访问属性...")
            result_dict = {}
            if hasattr(result, 'intent'):
                intent_obj = result.intent
                if hasattr(intent_obj, 'name'):
                    result_dict["intent"] = {
                        "name": intent_obj.name,
                        "confidence": getattr(intent_obj, "confidence", 0.3)
                    }
                else:
                    result_dict["intent"] = intent_obj
            else:
                result_dict["intent"] = {"name": "nlu_fallback", "confidence": 0.3}
            
            result_dict["entities"] = getattr(result, "entities", [])
            result_dict["intent_ranking"] = getattr(result, "intent_ranking", [])
        
        logger.info(f"格式化后的结果字典: {result_dict}")
        
        # 提取意图信息
        intent_data = result_dict.get("intent", {})
        logger.info(f"意图数据: {intent_data}, 类型: {type(intent_data)}")
        
        if isinstance(intent_data, dict):
            intent_name = intent_data.get("name", "nlu_fallback")
            intent_confidence = intent_data.get("confidence", 0.3)
        elif hasattr(intent_data, "name"):
            # 如果 intent 是对象
            intent_name = getattr(intent_data, "name", "nlu_fallback")
            intent_confidence = getattr(intent_data, "confidence", 0.3)
        else:
            logger.warning(f"无法解析意图数据: {intent_data}")
            intent_name = "nlu_fallback"
            intent_confidence = 0.3
        
        # 提取实体信息
        entities_data = result_dict.get("entities", [])
        entity_results = []
        for entity in entities_data:
            if isinstance(entity, dict):
                entity_results.append(EntityResult(
                    entity=entity.get("entity", ""),
                    value=entity.get("value", ""),
                    start=entity.get("start", 0),
                    end=entity.get("end", 0),
                    confidence=entity.get("confidence", 1.0)
                ))
            elif hasattr(entity, "entity"):
                entity_results.append(EntityResult(
                    entity=getattr(entity, "entity", ""),
                    value=getattr(entity, "value", ""),
                    start=getattr(entity, "start", 0),
                    end=getattr(entity, "end", 0),
                    confidence=getattr(entity, "confidence", 1.0)
                ))
        
        # 提取意图排名
        intent_ranking = result_dict.get("intent_ranking", [])
        formatted_ranking = []
        
        for ranking in intent_ranking[:5]:
            if isinstance(ranking, dict):
                formatted_ranking.append({
                    "name": ranking.get("name", ""),
                    "confidence": float(ranking.get("confidence", 0.0))
                })
            elif hasattr(ranking, "name"):
                formatted_ranking.append({
                    "name": getattr(ranking, "name", ""),
                    "confidence": float(getattr(ranking, "confidence", 0.0))
                })
        
        logger.info(f"最终返回: intent={intent_name}, confidence={intent_confidence}, entities={len(entity_results)}, ranking={len(formatted_ranking)}")
        
        response = NLUResponse(
            text=input.text,
            intent=IntentResult(name=intent_name, confidence=float(intent_confidence)),
            entities=entity_results,
            intent_ranking=formatted_ranking
        )
        
        logger.info("响应对象创建成功，准备返回")
        return response
        
    except Exception as e:
        logger.error(f"格式化返回结果失败: {e}", exc_info=True)
        logger.error(f"原始结果类型: {type(result)}")
        logger.error(f"原始结果: {result}")
        raise HTTPException(
            status_code=500,
            detail=f"格式化返回结果失败: {str(e)}"
        )
