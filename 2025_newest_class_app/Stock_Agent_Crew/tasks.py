from crewai import Task
from textwrap import dedent

class AnalysisTasks:
    
    def research(self, agent, company):
        return Task(
            description=dedent(
                f"""
                正在搜索並總結最新的{company}公司動態和新聞。
                特別關注最近發生的重大事件。
                """
            ),
            async_execution = True,
            agent=agent,
            expected_output="用列表的形式總結頭5項最重要的公司新聞。"
        )
    
    def analysis(self, agent, context):
        return Task(
            description=dedent(
                f"""
                將搜索到的信息進行分析，並且總結。
                """
            ),
            agent=agent,
            context = [context],
            expected_output="用報告的形式總結該公司的市場和走向，最終得出是否應該買入該公司股票的建議。"
        )