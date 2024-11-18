from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

@CrewBase
class stockCrew():
    """stock crew"""
    
    def __init__(self):
        self.ticker = None  # Inicializa o atributo ticker
        
    def set_ticker(self, ticker):
        """Set the ticker value"""
        self.ticker = ticker
        return self

    @agent
    def researcher(self) -> Agent:
        return Agent(
            llm='gpt-4o-mini',
            config=self.agents_config['researcher'],
            tools=[SerperDevTool(country="br",n_results=5,)],
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )

    @agent
    def audit_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['audit_analyst'],
            verbose=True
        )
    
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
        )
    
    @task
    def audit_task(self) -> Task:
        """Creates an audit task with filename including ticker"""
        current_time = datetime.now()
        filename = f"{self.ticker}_{current_time.strftime('%m%d_%H%M')}.md"
        
        return Task(
            config=self.tasks_config['audit_task'],
            output_file=filename,
            depends_on=['reporting_task']  # Garante que o audit_task dependa do reporting_task
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the stock crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
