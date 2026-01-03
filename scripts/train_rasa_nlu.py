"""Rasa NLU 模型训练脚本"""

import sys
import subprocess
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


def train_model():
    """训练 Rasa NLU 模型"""
    print("开始训练 Rasa NLU 模型...")
    
    # 路径配置
    rasa_data_dir = BASE_DIR / "rasa_data"
    models_dir = BASE_DIR / "models"
    config_path = rasa_data_dir / "config.yml"
    nlu_data_path = rasa_data_dir / "nlu.yml"
    
    # 检查文件是否存在
    if not nlu_data_path.exists():
        raise FileNotFoundError(f"训练数据文件不存在: {nlu_data_path}")
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    # 创建模型目录
    models_dir.mkdir(exist_ok=True)
    
    try:
        # 使用 Rasa 命令行工具训练 NLU 模型
        # 创建临时 domain.yml（Rasa 3.x 需要，但只训练 NLU 时可以简化）
        domain_path = rasa_data_dir / "domain.yml"
        if not domain_path.exists():
            print("创建临时 domain.yml 文件...")
            domain_content = """version: "3.1"

intents:
  - greet
  - query_order
  - check_inventory
  - create_return
"""
            domain_path.write_text(domain_content, encoding="utf-8")
        
        print(f"训练数据目录: {rasa_data_dir}")
        print(f"配置文件: {config_path}")
        print("开始训练模型（这可能需要几分钟）...")
        
        # 使用 Rasa CLI 训练 NLU 模型
        # 注意：Rasa 3.x 的 train nlu 命令可能需要 domain 文件
        cmd = [
            sys.executable,
            "-m",
            "rasa",
            "train",
            "nlu",
            "--config", str(config_path),
            "--nlu", str(nlu_data_path),
            "--domain", str(domain_path),
            "--out", str(models_dir),
            "--fixed-model-name", "latest_nlu"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=str(BASE_DIR),
            check=True,
            capture_output=False
        )
        
        model_path = models_dir / "latest_nlu.tar.gz"
        
        if model_path.exists():
            print(f"\n✅ 模型训练完成！")
            print(f"模型文件: {model_path}")
            print(f"\n现在可以启动 FastAPI 服务了:")
            print(f"  make dev")
            print(f"  或")
            print(f"  uv run uvicorn app.main:app --reload")
        else:
            print(f"\n⚠️  警告: 模型文件未找到，但训练过程已完成")
            print(f"请检查 {models_dir} 目录")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 训练失败: Rasa 训练命令执行失败")
        print(f"错误代码: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    train_model()
