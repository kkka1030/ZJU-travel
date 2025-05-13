import asyncio
import os
import sys
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import Swarm, RoundRobinGroupChat, SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.conditions import HandoffTermination, MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
from autogen_agentchat.tools import AgentTool
from dotenv import load_dotenv
from utils.Console_with_history import *

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



async def main():

    # 创建老师代理
    teacher = AssistantAgent(
        name='Fund_Teacher',
        model_client=model_client,
        system_message='''
        你是一个基金投资专家，精通一切基金投资相关的知识。
        你会根据用户请求给出基金投资的建议和指导，帮助用户更好地进行基金投资。
        你会将用户知识以通俗直白地方式表达出来，帮助入门级投资者理解。
        
        ''',
    )
    web_surfer = MultimodalWebSurfer(
        name="MultimodalWebSurfer",
        headless=True,
        model_client=model_client,
        debug_dir="./debug",
        to_save_screenshots=False,
        start_page="https://www.google.com",
        browser_channel="chrome",
        
    )

    web_surfer_tool = AgentTool(agent=web_surfer)
    
    web_surfer_agent = AssistantAgent(
        name="Web_Surfer",
        model_client=model_client,
        tools=[web_surfer_tool],
        system_message=
        "你是一个专业旅行顾问，根据用户对话动态规划行程。你配备了一个网页搜索工具，可以浏览网页以查找酒店、景点、交通等信息。"
        "不要生成任何图像" \
        "你可以调用网页搜索工具在网上搜索信息。如果没有找到信息，你可以再次调用它。请在提供信息时，每次生成引用时，包含一个有效的URL链接。" \
        "当你找到信息时，请总结它并说'终止。'",
        reflect_on_tool_use=True
    )
    # 将用户输入创建为学生代理
    student = UserProxyAgent(
        name='Student',
    )

    # 设置终止条件
    termination = TextMentionTermination(sources=["Student"],text="再见")

    # 创建轮询团队
    team = RoundRobinGroupChat(
        participants=[web_surfer_agent, student],
        termination_condition=termination,
    )
    _, result = await Console_with_history(
        stream=team.run_stream(task="人机对话启动"),
        output_stats=True,
    )

    chat_history = [item for item in result if item.type == 'TextMessage']

    return chat_history

if __name__ == "__main__":
    chat_history = asyncio.run(main())
    for message in chat_history:
        print(f"{message.source}: {message.content}")