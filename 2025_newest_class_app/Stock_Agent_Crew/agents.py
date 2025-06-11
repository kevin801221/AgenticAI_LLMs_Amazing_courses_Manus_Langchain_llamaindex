from crewai import Agent
from tools.search import SearchTools

class AnalysisAgents:
    
    def __init__(self, llm):
        self.llm = llm

    def market_research_analyst(self):
        return Agent(
            llm=self.llm,
            role="市場研究分析師",
            goal="搜索公司的市場和財務狀況，並按照找到的信息整理總結出公司各方面的表現和財務狀況",
            backstory="最富經驗的市場研究分析師，善於捕捉和發掘公司內在的真相。請用中文思考和行動，並用中文回覆客戶問題或與其他同事交流。",
            tools=[SearchTools.searchInfo],
            allow_delegation=False,
            max_iter=3,
            verbose=True
        )
    
    #特許財務分析師
    def cfa(self):
        return Agent(
            llm=self.llm,
            role="特許財務分析師",
            goal="根據市場研究分析師搜索到的資料，重新整理並總結出公司的狀況，並且提供該公司的股份是否值得買入的建議",
            backstory="最富經驗的投資者，善於透過公司細微的變化，捕捉公司股價走向。現在你面對一生中最中的客戶。請用中文思考和行動，並用中文回覆客戶問題或與其他同事交流。",
            tools=[],
            allow_delegation=False,
            verbose=True
        )