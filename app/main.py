"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import json
import logging
from app.api.nlu_router import router as nlu_router
from app.core.rasa_loader import RasaNLULoader

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    在启动时加载模型，在关闭时清理资源
    """
    # 启动时：加载 Rasa 模型
    print("正在加载 Rasa NLU 模型...")
    try:
        RasaNLULoader.get_agent()
        print("✅ Rasa NLU 模型加载完成！")
    except Exception as e:
        print(f"⚠️  模型加载失败: {e}")
        print("⚠️  服务将启动，但意图识别功能可能不可用")
    
    yield
    
    # 关闭时：清理资源（如果需要）
    print("正在关闭服务...")


app = FastAPI(
    title="ERP Rasa NLU 意图识别服务",
    description="为ERP系统提供自然语言意图识别能力",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加请求体日志中间件（用于调试）
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 只记录 POST 请求
        if request.method == "POST":
            try:
                # 读取请求体（注意：读取后需要重新创建请求对象）
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8', errors='replace')
                    logger.info(f"收到请求体 (前200字符): {body_str[:200]}")
                
                # 重新创建请求对象，以便后续处理可以读取请求体
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
            except Exception as e:
                logger.warning(f"无法读取请求体: {e}")
        
        response = await call_next(request)
        return response

app.add_middleware(RequestLoggingMiddleware)


# 添加请求验证错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误，提供更详细的错误信息"""
    try:
        body = await request.body()
        body_str = body.decode('utf-8', errors='replace') if body else None
    except Exception as e:
        logger.error(f"读取请求体失败: {e}")
        body_str = None
    
    logger.error(f"请求验证失败: {exc.errors()}, 请求体: {body_str[:200] if body_str else None}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求参数验证失败",
            "errors": exc.errors(),
            "body_preview": body_str[:200] if body_str else None,
            "hint": "请确保 JSON 格式正确，且包含 'text' 字段。在 Windows Git Bash 中，建议使用文件方式：curl -X POST http://127.0.0.1:8200/nlu/predict -H 'Content-Type: application/json' -d @request.json"
        }
    )


# 添加 Starlette HTTP 异常处理（包括 JSON 解析错误）
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """处理 HTTP 异常，包括 JSON 解析错误"""
    if exc.status_code == 400:
        try:
            body = await request.body()
            body_str = body.decode('utf-8', errors='replace') if body else None
        except Exception as e:
            logger.error(f"读取请求体失败: {e}")
            body_str = None
        
        logger.error(f"请求解析失败 (400): {exc.detail}, 请求体: {body_str[:200] if body_str else None}")
        
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.detail or "请求解析失败",
                "body_preview": body_str[:200] if body_str else None,
                "hint": "请检查 JSON 格式是否正确。在 Windows Git Bash 中，多行 JSON 可能有问题，建议使用文件方式：curl -X POST http://127.0.0.1:8200/nlu/predict -H 'Content-Type: application/json' -d @request.json"
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(f"未处理的异常: {type(exc).__name__}: {exc}", exc_info=True)
    
    try:
        body = await request.body()
        body_str = body.decode('utf-8', errors='replace') if body else None
    except Exception:
        body_str = None
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"服务器内部错误: {str(exc)}",
            "body_preview": body_str[:200] if body_str else None,
            "hint": "如果这是 JSON 解析错误，请检查 JSON 格式。在 Windows Git Bash 中，建议使用文件方式发送请求。"
        }
    )

app.include_router(nlu_router)


@app.get("/")
async def root():
    """健康检查接口"""
    return {"message": "ERP Rasa NLU Service is running!"}
