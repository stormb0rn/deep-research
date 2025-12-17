"""
Google Gemini Deep Research 示例
使用 Interactions API 进行深度研究
"""

import os
import re
import time
from datetime import datetime
from pathlib import Path
from google import genai


class DeepResearcher:
    """Deep Research 封装类"""

    AGENT = 'deep-research-pro-preview-12-2025'
    REPORTS_DIR = Path(__file__).parent / "reports"

    def __init__(self, api_key: str = None, reports_dir: str = None):
        """
        初始化 Deep Research 客户端

        Args:
            api_key: Gemini API Key，如果不提供则从环境变量 GEMINI_API_KEY 读取
            reports_dir: 报告保存目录，默认为 ./reports
        """
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

        if reports_dir:
            self.reports_dir = Path(reports_dir)
        else:
            self.reports_dir = self.REPORTS_DIR

        # 确保报告目录存在
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, query: str) -> str:
        """
        根据研究主题生成文件名

        Args:
            query: 研究问题

        Returns:
            文件名 (不含扩展名)
        """
        # 提取前60个字符作为主题
        topic = query.strip()[:60]

        # 移除或替换特殊字符
        topic = re.sub(r'[\\/*?:"<>|\n\r\t]', '', topic)
        topic = re.sub(r'\s+', '_', topic)
        topic = topic.strip('_.')

        # 添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"{topic}_{timestamp}"

    def _save_report(self, query: str, report: str) -> Path:
        """
        保存研究报告

        Args:
            query: 研究问题
            report: 报告内容

        Returns:
            保存的文件路径
        """
        filename = self._generate_filename(query)
        filepath = self.reports_dir / f"{filename}.md"

        # 在报告开头添加元信息
        header = f"""# Research Report

**Query:** {query.strip()}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(header + report)

        return filepath

    def research(self, query: str, stream: bool = True, save: bool = True) -> tuple[str, Path | None]:
        """
        执行深度研究

        Args:
            query: 研究问题
            stream: 是否使用流式输出（实时显示进度）
            save: 是否自动保存报告到文件

        Returns:
            (研究报告文本, 保存的文件路径) - 如果 save=False，文件路径为 None
        """
        if stream:
            report = self._stream_research(query)
        else:
            report = self._poll_research(query)

        filepath = None
        if save and report:
            filepath = self._save_report(query, report)
            print(f"\n📄 报告已保存: {filepath}")

        return report, filepath

    def _poll_research(self, query: str) -> str:
        """轮询方式获取研究结果"""
        print(f"开始研究: {query[:50]}...")

        interaction = self.client.interactions.create(
            input=query,
            agent=self.AGENT,
            background=True
        )

        print(f"任务 ID: {interaction.id}")

        while True:
            interaction = self.client.interactions.get(interaction.id)
            status = interaction.status

            if status == "completed":
                print("✅ 研究完成!")
                return interaction.outputs[-1].text
            elif status == "failed":
                raise Exception(f"研究失败: {interaction.error}")

            print(f"⏳ 状态: {status}")
            time.sleep(10)

    def _stream_research(self, query: str) -> str:
        """流式方式获取研究结果（实时输出）"""
        print(f"开始研究: {query[:50]}...")
        print("-" * 50)

        result_parts = []

        stream = self.client.interactions.create(
            input=query,
            agent=self.AGENT,
            background=True,
            stream=True,
            agent_config={
                "type": "deep-research",
                "thinking_summaries": "auto"
            }
        )

        for event in stream:
            if event.event_type == "interaction.start":
                print(f"任务 ID: {event.interaction.id}\n")

            elif event.event_type == "content.delta":
                if event.delta.type == "text":
                    text = event.delta.text
                    print(text, end="", flush=True)
                    result_parts.append(text)
                elif event.delta.type == "thought_summary":
                    print(f"\n💭 思考: {event.delta.content.text}\n")

            elif event.event_type == "interaction.complete":
                print("\n" + "-" * 50)
                print("✅ 研究完成!")
                break

            elif event.event_type == "error":
                raise Exception(f"研究出错: {event}")

        return "".join(result_parts)


def example_simple():
    """简单示例：轮询方式"""
    researcher = DeepResearcher()

    query = "2025年最流行的 AI Agent 框架有哪些？比较它们的优缺点。"
    report, filepath = researcher.research(query, stream=False)

    print("\n" + "=" * 50)
    print("研究报告:")
    print("=" * 50)
    print(report[:500] + "..." if len(report) > 500 else report)


def example_stream():
    """流式示例：实时输出"""
    researcher = DeepResearcher()

    query = """
    Research the current state of quantum computing in 2025.

    Please include:
    1. Major players and their latest achievements
    2. Technical breakthroughs
    3. Commercial applications
    4. Future outlook
    """

    report, filepath = researcher.research(query, stream=True)
    # 报告会自动保存到 reports/ 目录


def example_formatted():
    """格式化输出示例"""
    researcher = DeepResearcher()

    query = """
    Research the competitive landscape of Large Language Models in 2025.

    Format the output as a technical report with:
    1. Executive Summary (2-3 paragraphs)
    2. Key Players Comparison Table (include model name, parameters, benchmark scores)
    3. Technical Analysis
    4. Market Trends
    5. Conclusions
    """

    report, filepath = researcher.research(query, stream=True)
    return report, filepath


def interactive_research():
    """交互式研究：用户输入研究主题"""
    researcher = DeepResearcher()

    print("=" * 50)
    print("Google Gemini Deep Research - 交互模式")
    print("=" * 50)
    print("输入你想研究的主题，输入 'quit' 退出\n")

    while True:
        query = input("🔍 研究主题: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            print("再见！")
            break

        if not query:
            print("请输入研究主题\n")
            continue

        try:
            report, filepath = researcher.research(query, stream=True)
            print(f"\n✅ 研究完成！报告已保存到: {filepath}\n")
        except Exception as e:
            print(f"\n❌ 研究失败: {e}\n")


if __name__ == "__main__":
    import sys

    # 检查 API Key
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ 请设置环境变量 GEMINI_API_KEY")
        print("   export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    # 默认运行交互模式
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "simple":
            example_simple()
        elif mode == "formatted":
            example_formatted()
        elif mode == "stream":
            example_stream()
        elif mode == "interactive" or mode == "-i":
            interactive_research()
        else:
            # 直接将参数作为研究主题
            query = " ".join(sys.argv[1:])
            researcher = DeepResearcher()
            report, filepath = researcher.research(query, stream=True)
    else:
        interactive_research()
