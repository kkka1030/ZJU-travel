import asyncio
import os
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from utils.Console_with_history import Console_with_history
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.tools import AgentTool
from autogen_agentchat.agents import AssistantAgent
from dotenv import load_dotenv


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("CUSTOM_API_KEY")
CUSTOM_API_KEY = os.environ.get("CUSTOM_API_KEY") 
model_client = OpenAIChatCompletionClient(
    model="gpt-3.5-turbo", 
    base_url="https://api.zchat.tech/v1",
    api_key=CUSTOM_API_KEY, 
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
    }
)

async def web_surfer() -> None:
    web_surfer = MultimodalWebSurfer(
        name="MultimodalWebSurfer",
        headless=True,
        model_client=model_client,
        debug_dir="./debug",
        to_save_screenshots=True,
        start_page="https://www.google.com",
        browser_channel="chrome",
    )

    web_surfer_tool = AgentTool(agent=web_surfer)
    
    web_surfer_agent = AssistantAgent(
        name="Web_Surfer",
        model_client=model_client,
        tools=[web_surfer_tool],
        system_message=
        "你是一个网页浏览代理。你配备了一个网页搜索工具，可以浏览网页以查找信息。" \
        "你可以调用网页搜索工具在网上搜索信息。如果没有找到信息，你可以再次调用它。" \
        "当你找到信息时，请总结它并说'终止。'" ,
        reflect_on_tool_use=True
    )

    termination = MaxMessageTermination(10) | TextMentionTermination('TERMINATE.')
    
    agent_team = RoundRobinGroupChat(
        participants=[web_surfer_agent], 
        termination_condition=termination,
    )

    # Run the team and stream messages to the console
    stream = agent_team.run_stream(task="精确查找特朗普政府对中国的历史关税政策(直到2025.4.25)，按时间顺序给出，再查找美国历史上类似的关税政策")
    await Console_with_history(stream)

if __name__ == "__main__":
    asyncio.run(web_surfer())
