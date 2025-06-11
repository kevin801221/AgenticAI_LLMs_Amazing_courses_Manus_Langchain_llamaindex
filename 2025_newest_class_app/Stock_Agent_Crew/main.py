from crewai import Crew, Process,LLM

from agents import AnalysisAgents
from tasks import AnalysisTasks

llm = LLM(
    model="ollama/llama3.1:latest",
    base_url="http://localhost:11434",
)

class FinancialCrew:

    def __init__(self, company: str):
        self.company = company

    def run(self):

        agents = AnalysisAgents(llm)
        tasks = AnalysisTasks()

        mr_analyst = agents.market_research_analyst()
        cfa = agents.cfa()

        research = tasks.research(mr_analyst, self.company)
        analysis = tasks.analysis(cfa, research)

        crew = Crew(
            agents=[mr_analyst, cfa],
            tasks=[research, analysis],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()

        return result


if __name__ == "__main__":
    print("\n\n## 歡迎來到投資顧問團隊")
    print("-------------------------")
    company = input("請輸入您想分析的公司名稱\n")

    financial_crew = FinancialCrew(company)
    result = financial_crew.run()
    print("\n\n####################")
    print("## 如下是分析結果")
    print("####################\n")
    print(result)