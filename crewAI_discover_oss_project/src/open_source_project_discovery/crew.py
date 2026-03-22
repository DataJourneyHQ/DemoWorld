import os
import json
from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	SerperDevTool,
	ScrapeWebsiteTool
)


from pydantic import BaseModel
from jambo import SchemaConverter

def _make_llm(**kwargs) -> LLM:
    """Build an LLM instance, honouring GitHub Models env vars when present."""
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        kwargs["api_key"] = github_token
        kwargs["base_url"] = "https://models.inference.ai.azure.com"
        # swap openai/ prefix → github_ai/ so LiteLLM routes correctly
        if "model" in kwargs and kwargs["model"].startswith("openai/"):
            kwargs["model"] = kwargs["model"].replace("openai/", "github_ai/", 1)
    return LLM(**kwargs)

@CrewBase
class OpenSourceProjectDiscoveryCrew:
    """OpenSourceProjectDiscovery crew"""

    
    @agent
    def open_source_project_discovery_specialist(self) -> Agent:
        
        return Agent(
            config=self.agents_config["open_source_project_discovery_specialist"],
            
            
            tools=[				SerperDevTool(),
				ScrapeWebsiteTool()],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            
            
            max_execution_time=None,
            llm=_make_llm(model="openai/gpt-4o-mini", temperature=0.7),
            response_format=self._load_response_format("open_source_project_discovery_specialist"),
        )
    

    
    @task
    def discover_and_evaluate_open_source_projects(self) -> Task:
        return Task(
            config=self.tasks_config["discover_and_evaluate_open_source_projects"],
            markdown=False,
            
            
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the OpenSourceProjectDiscovery crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            chat_llm=_make_llm(model="openai/gpt-4o-mini"),
        )


    def _load_response_format(self, name):
        with open(os.path.join(self.base_directory, "config", f"{name}.json")) as f:
            json_schema = json.loads(f.read())

        return SchemaConverter.build(json_schema)

