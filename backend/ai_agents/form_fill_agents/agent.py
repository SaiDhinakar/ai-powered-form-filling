from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from ai_agents.tools.translator import translate

translate_tool = FunctionTool(
    translate,  
    # name="translate",
    # description="Translate text from source language to English"
)

lingua_fix_agent = Agent(
    name="lingua_fix_agent",
    model="gemini-2.5-flash",
    description="Multilingual spelling correction and translation agent",
    instruction="""
You are a multilingual text normalization agent.

Input arguments:
- input_text: text in any language
- lang: source language code (or 'auto')

Steps you MUST follow:
1. Correct spelling, grammar, and spacing in the ORIGINAL language.
2. Do NOT translate yet.
3. Pass the corrected text to the translate tool with dest='en'.
4. Return ONLY the final translated English text.
5. Do not explain your steps.
""",
    tools=[translate_tool],
)
