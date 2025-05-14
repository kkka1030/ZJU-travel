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
os.environ["SERPER_API_BASE"] = os.getenv("SERPER_URL")

llm_config = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.5,
    "api_key": os.getenv("CUSTOM_API_KEY"),
    "base_url": os.getenv("BASE_URL"),
    "api_type": "openai"
}

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

def get_serper_search_results(query):
    payload = {
        "q": query,
        "gl": "cn",
        "hl": "zh-cn",
        "type": "search",
        "engine": "google"
    }
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    
    response = requests.post(os.getenv("SERPER_URL"), json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {}
    
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    
    if not user_input:
        return jsonify({"reply": "请输入内容"})

    chat_history.append({"role": "user", "content": user_input})
    reply_text = ""

    try:
        if any(kw in user_input for kw in ["航班", "酒店", "路线", "查一下", "门票", "交通"]):
            search_results = get_serper_search_results(user_input)
            reply_text += "<strong>[搜索助手]</strong><br>"
            if search_results:
                answer_box = search_results.get("answerBox", None)
                if answer_box:
                    snippet = answer_box.get("snippet", "")
                    link = answer_box.get("link", "")
                    answer_box_text = f"{snippet}<br><br>"
                    if link:
                        answer_box_text += f"<strong>查看更多信息：</strong><a href='{link}'>{link}</a><br><br>"
                else:
                    answer_box_text = ""

                organic_results = search_results.get("organic", [])
                organic_text = "以下是搜索结果<br>"
                for result in organic_results:
                    organic_text += f"标题：{result['title']}<br><a href='{result['link']}'>链接</a><br>{result['snippet']}<br><br>"

                reply_text += answer_box_text + organic_text
            else:
                reply_text = "<strong>[搜索助手]</strong> 没有找到相关的搜索结果。<br><br>"

        assistant_reply = assistant.generate_reply(chat_history)
        assistant_text = assistant_reply.content if hasattr(assistant_reply, "content") else str(assistant_reply)
        reply_text += f"<strong>[旅行顾问]</strong> {assistant_text}"

        chat_history.append({"role": "assistant", "name": "travel_assistant", "content": assistant_text})

        return jsonify({"reply": reply_text})

    except Exception as e:
        return jsonify({"reply": f"<strong>[系统]</strong> 出错了：{str(e)}"}), 500

@app.route("/<page>.html")
def serve_page(page):
    try:
        return render_template(f"{page}.html")
    except:
        return f"<h3>未找到页面：{page}.html</h3>", 404

if __name__ == "__main__":
    app.run(debug=True)