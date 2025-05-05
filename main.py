from flask import Flask, request, jsonify, render_template, redirect, url_for
from autogen import AssistantAgent
from autogen.agentchat.contrib.web_surfer import WebSurferAgent
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("CUSTOM_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("BASE_URL")
os.environ["OPENAI_API_TYPE"] = "openai"
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

llm_config = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.5,
    "api_key": os.getenv("CUSTOM_API_KEY"),
    "base_url": os.getenv("BASE_URL"),
    "api_type": "openai"
}

search_agent = WebSurferAgent(
    name="test_search",
    llm_config=llm_config,
    system_message="你是联网搜索助手"
)

assistant = AssistantAgent(
    name="travel_assistant",
    llm_config=llm_config,
    system_message="你是一个专业旅行顾问，根据用户对话动态规划行程。"
)

chat_history = [{"role": "system", "content": "你是一个旅行顾问，协助用户多轮制定旅行计划。"}]

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("chat.html")



@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"reply": "请输入内容"})
    chat_history.append({"role": "user", "content": user_input})
    reply_text = ""
    try:
        if any(kw in user_input for kw in ["航班", "酒店", "路线", "查一下", "门票", "交通"]):
            search_prompt = f"请帮我搜索：{user_input}"
            search_reply = search_agent.generate_reply([{"role": "user", "content": search_prompt}])
            search_text = search_reply.content if hasattr(search_reply, "content") else str(search_reply)
            chat_history.append({"role": "assistant", "name": "search_agent", "content": search_text})
            reply_text += f"<strong>[搜索助手]</strong> {search_text}<br><br>"
        assistant_reply = assistant.generate_reply(chat_history)
        assistant_text = assistant_reply.content if hasattr(assistant_reply, "content") else str(assistant_reply)
        reply_text += f"<strong>[旅行顾问]</strong> {assistant_text}"
        chat_history.append({"role": "assistant", "name": "travel_assistant", "content": assistant_text})
        return jsonify({"reply": reply_text})
    except Exception as e:
        return jsonify({"reply": f"<strong>[系统]</strong> 出错了：{str(e)}"}), 500

from flask import send_from_directory

@app.route("/<page>.html")
def serve_page(page):
    try:
        return render_template(f"{page}.html")
    except:
        return f"<h3>未找到页面：{page}.html</h3>", 404
import requests

@app.route("/api/weather")
def get_weather():
    city = request.args.get("city", "Hangzhou")
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=zh_cn&units=metric"

    try:
        res = requests.get(url)
        data = res.json()
        if res.status_code != 200:
            return jsonify({"error": data.get("message", "无法获取天气")}), 400

        result = {
            "城市": city,
            "天气": data["weather"][0]["description"],
            "温度": data["main"]["temp"],
            "体感温度": data["main"]["feels_like"],
            "风速": data["wind"]["speed"]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
