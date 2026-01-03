.PHONY: help install train run dev test clean lint format

# 默认目标
.DEFAULT_GOAL := help

# 变量定义
PYTHON := python
UV := uv
VENV := .venv
APP := app.main:app
PORT := 8200
HOST := 0.0.0.0

## help: 显示帮助信息
help:
	@echo "ERP 智能意图识别服务 - Makefile 命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make install      - 创建虚拟环境并安装依赖"
	@echo "  make train        - 训练 Rasa NLU 模型"
	@echo "  make run          - 启动生产环境服务"
	@echo "  make dev          - 启动开发环境服务（带热重载）"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 代码检查（ruff）"
	@echo "  make format       - 代码格式化（black）"
	@echo "  make clean        - 清理临时文件和缓存"
	@echo "  make clean-all    - 清理所有生成的文件（包括模型）"
	@echo "  make help         - 显示此帮助信息"
	@echo ""

## install: 创建虚拟环境并安装依赖
install:
	@echo "创建虚拟环境..."
	$(UV) venv
	@echo "安装项目依赖..."
	$(UV) pip install -e .
	@echo "✅ 安装完成！"

## install-dev: 安装开发依赖
install-dev:
	@echo "安装开发依赖..."
	$(UV) pip install -e ".[dev]"
	@echo "✅ 开发依赖安装完成！"

## train: 训练 Rasa NLU 模型
train:
	@echo "开始训练 Rasa NLU 模型..."
	$(UV) run $(PYTHON) scripts/train_rasa_nlu.py
	@echo "✅ 模型训练完成！"

## run: 启动生产环境服务
run:
	@echo "启动生产环境服务..."
	$(UV) run uvicorn $(APP) --host $(HOST) --port $(PORT) --workers 4

## dev: 启动开发环境服务（带热重载）
dev:
	@echo "启动开发环境服务（热重载模式）..."
	$(UV) run uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

## test: 运行测试
test:
	@echo "运行测试..."
	$(UV) run pytest tests/ -v
	@echo "✅ 测试完成！"

## lint: 代码检查（ruff）
lint:
	@echo "运行代码检查..."
	$(UV) run ruff check app/ scripts/
	@echo "✅ 代码检查完成！"

## format: 代码格式化（black）
format:
	@echo "格式化代码..."
	$(UV) run black app/ scripts/
	@echo "✅ 代码格式化完成！"

## format-check: 检查代码格式（不修改）
format-check:
	@echo "检查代码格式..."
	$(UV) run black --check app/ scripts/

## clean: 清理临时文件和缓存
clean:
	@echo "清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	@echo "✅ 清理完成！"

## clean-all: 清理所有生成的文件（包括模型）
clean-all: clean
	@echo "清理模型文件..."
	rm -f models/*.tar.gz 2>/dev/null || true
	rm -f models/*.tar 2>/dev/null || true
	@echo "✅ 全部清理完成！"

## check: 检查项目状态
check:
	@echo "检查项目状态..."
	@echo "Python 版本:"
	@$(UV) run $(PYTHON) --version
	@echo ""
	@echo "已安装的包:"
	@$(UV) pip list
	@echo ""
	@if [ -f "models/latest_nlu.tar.gz" ]; then \
		echo "✅ 模型文件存在"; \
	else \
		echo "⚠️  模型文件不存在，请运行 'make train' 训练模型"; \
	fi

## setup: 完整设置（安装依赖 + 训练模型）
setup: install train
	@echo "✅ 项目设置完成！"
	@echo "现在可以运行 'make dev' 启动开发服务器"
