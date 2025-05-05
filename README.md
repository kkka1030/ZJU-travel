# 旅行AI助手

一个基于 Flask 构建的中文旅行对话助手，结合大模型与联网搜索功能，支持多轮对话规划旅行，还集成天气预警、学校介绍、导航界面与旅行计划等模块，带有现代化 UI 界面，支持登录、模块化页面导航。

---

## 功能特点

- **AI多轮对话**：基于大模型自动规划旅行内容
- **联网搜索**：对航班、酒店、门票等问题可自动触发搜索
- **多页面支持**：天气预警、浙江大学介绍、地图导航、旅行计划表
- **天气API接入**：自动显示杭州实时天气
- **登录页面**：模拟登录入口，未来可扩展为用户系统
- **响应式美观UI**：Bootstrap + 自定义样式

---

## 安装说明



### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量 `.env`
```
CUSTOM_API_KEY=你的OpenAI API Key
BASE_URL=https://api.openai.com/v1
SERPER_API_KEY=你的联网搜索Key

```

### 3. 启动服务
```bash
python main.py
```
访问：http://127.0.0.1:5000/

---

## 项目结构
```
travel-ai-assistant/
├── main.py
├── .env
├── templates/
│   ├── chat.html           # 主UI入口（含侧边导航）
│   ├── weather.html        # 天气模块
│   ├── zju.html            # 浙江大学介绍
│   ├── map.html            # 地图界面（占位）
│   └── plan.html           # 旅行计划表
├── static/                # 静态文件目录（CSS/图片等）
└── requirements.txt       # Python依赖
```

---

## 示例截图
（请根据运行结果补充截图）

---

## 未来可扩展方向
- 用户注册与行程历史保存
- 地图路径规划（接入高德/百度）
- AI 推荐酒店/航班卡片展示
- 行程生成 PDF/导出功能
- 接入天气api
---

## License
MIT License

---

欢迎提交 PR 或 issue 进行优化！

