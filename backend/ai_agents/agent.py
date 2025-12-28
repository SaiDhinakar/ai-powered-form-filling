from google.adk.agents.llm_agent import Agent
from ai_agents.form_fill_agents.agent import lingua_fix_agent

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="Root dispatcher agent",
    instruction="""
You are the root agent.

Delegate text normalization requests to the lingua_fix_agent.
""",
    sub_agents=[lingua_fix_agent],
)
