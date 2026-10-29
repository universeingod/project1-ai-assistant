1.**概述**：一个基于 Streamlit 的个人 AI 助手，支持多轮对话、跨会话记忆（JSON 持久化）和函数调用（计算器工具），后端接 DeepSeek API。

2.**功能清单**：多轮对话/持久化记忆/工具调用（计算器）

3.**技术栈**：Streamlit · OpenAI SDK · DeepSeek API · Function Calling · python-dotenv

4.**架构图**：

```mermaid
flowchart TB
    subgraph 前端
        UI[Streamlit 网页]
    end
    subgraph 你的程序
        CL[OpenAI Client]
        TOOL[calculate]
        MEM[session_state 内存]
        DISK[(chat_history.json 磁盘)]
    end
    subgraph 模型
        LLM[DeepSeek API]
    end
    UI-->CL
    CL-->|① 发 messages+tools| LLM
    LLM-->|拿 tool_calls| CL
    CL-->TOOL
    TOOL-->|结果回填| CL
    CL-->|② 发完整 messages| LLM
    LLM-->|拿最终answer| UI
    MEM <-->|save/load| DISK
```
5.**截图**:
![算数](images/calc.png)
![普通问答](images/answer.png)

6.**快速开始**:
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入你的 DEEPSEEK_API_KEY
streamlit run app.py
