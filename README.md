# Deep Research

基于 Google Gemini Deep Research API 的深度研究工具，自动生成结构化研究报告。

## 功能特点

- 使用 Gemini `deep-research-pro-preview-12-2025` 模型进行深度研究
- 支持流式输出，实时查看研究进度和思考过程
- 自动保存研究报告为 Markdown 文件
- 提供交互式命令行模式

## 安装

```bash
# 克隆仓库
git clone https://github.com/stormb0rn/deep-research.git
cd deep-research

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 配置

1. 从 [Google AI Studio](https://aistudio.google.com/) 获取 API Key
2. 设置环境变量：

```bash
export GEMINI_API_KEY='your-api-key'
```

或复制 `.env.example` 为 `.env` 并填入 API Key。

## 使用方法

### 交互模式（默认）

```bash
python deep_research.py
```

### 直接指定研究主题

```bash
python deep_research.py "2025年最流行的 AI Agent 框架有哪些？"
```

### 其他模式

```bash
python deep_research.py simple      # 轮询模式示例
python deep_research.py stream      # 流式输出示例
python deep_research.py formatted   # 格式化报告示例
```

### 作为模块使用

```python
from deep_research import DeepResearcher

researcher = DeepResearcher()
report, filepath = researcher.research("你的研究问题", stream=True)
```

## 输出

研究报告自动保存在 `reports/` 目录下，文件名包含研究主题和时间戳。

## 依赖

- Python 3.10+
- google-genai >= 1.55.0

## License

MIT
