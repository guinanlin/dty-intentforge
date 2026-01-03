# ERP 智能意图识别服务

基于 FastAPI + Rasa NLU 的意图识别服务，为 ERP 系统提供自然语言意图识别能力。

## 功能特性

- 🎯 **意图识别**：识别用户输入的自然语言意图
- 🚀 **高性能**：模型推理延迟 < 200ms
- 📦 **轻量级**：模型体积小（30-100MB）
- 🔧 **易维护**：训练数据和服务代码集中管理
- 🌏 **中文支持**：专为中文场景优化

## 技术栈

- Python ≥ 3.9
- FastAPI：现代、快速的 Web 框架
- Rasa NLU：自然语言理解引擎
- uv：极速 Python 包管理工具

## 快速开始

### 前置要求

- Python ≥ 3.9
- uv（Python 包管理工具）
- make（可选，但推荐使用 Makefile）

### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 使用 Makefile（推荐）

项目提供了 Makefile 作为核心入口，简化常用操作：

```bash
# 查看所有可用命令
make help

# 完整设置（安装依赖 + 训练模型）
make setup

# 启动开发服务器（热重载）
make dev

# 启动生产服务器
make run

# 训练模型
make train

# 运行测试
make test

# 代码格式化
make format

# 代码检查
make lint
```

### 手动安装（不使用 Makefile）

```bash
# 克隆项目
git clone <your-repo> erp-rasa-nlu-service
cd erp-rasa-nlu-service

# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
uv pip install -e .

# 训练模型
uv run python scripts/train_rasa_nlu.py

# 启动服务
uv run uvicorn app.main:app --host 0.0.0.0 --port 8200 --reload
```

### 测试接口

**使用 curl**：
```bash
curl -X POST http://localhost:8200/nlu/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "帮我查一下订单12345的状态"}'
```

**访问 API 文档**：
- Swagger UI: http://localhost:8200/docs
- ReDoc: http://localhost:8200/redoc

## API 使用

### 意图识别接口

**接口路径**：`POST /nlu/predict`

**请求示例**：
```json
{
  "text": "帮我查一下订单12345的状态"
}
```

**响应示例**：
```json
{
  "text": "帮我查一下订单12345的状态",
  "intent": {
    "name": "query_order",
    "confidence": 0.98
  },
  "entities": [
    {
      "entity": "order_id",
      "value": "12345",
      "start": 7,
      "end": 12,
      "confidence": 0.95
    }
  ],
  "intent_ranking": [
    {"name": "query_order", "confidence": 0.98},
    {"name": "check_inventory", "confidence": 0.01},
    {"name": "greet", "confidence": 0.01}
  ]
}
```

## 项目结构

```
erp-rasa-nlu-service/
├── app/                    # FastAPI 应用代码
│   ├── api/               # API 路由
│   ├── core/              # 核心功能（配置、模型加载）
│   └── schemas/           # 数据模型
├── rasa_data/             # Rasa 训练数据
│   ├── nlu.yml           # 意图定义和训练示例
│   └── config.yml        # NLU pipeline 配置
├── models/                # 训练生成的模型
├── scripts/               # 训练脚本
└── pyproject.toml        # 项目配置和依赖

```

## 添加新意图

1. 编辑 `rasa_data/nlu.yml`，添加新意图和训练示例
2. 运行训练脚本：`uv run python scripts/train_rasa_nlu.py`
3. 重启 FastAPI 服务

## 开发

### 安装开发依赖

```bash
# 使用 Makefile
make install-dev

# 或手动安装
uv pip install -e ".[dev]"
```

### 代码格式化

```bash
# 使用 Makefile
make format      # 格式化代码
make format-check # 仅检查格式（不修改）
make lint        # 代码检查

# 或手动运行
uv run black app/ scripts/
uv run ruff check app/ scripts/
```

### 其他常用命令

```bash
make check       # 检查项目状态
make clean       # 清理临时文件
make clean-all   # 清理所有文件（包括模型）
```

## 许可证

MIT
