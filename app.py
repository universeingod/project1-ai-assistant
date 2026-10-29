import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import json
import re
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def calculate(expression: str) -> str:
    if not re.fullmatch(r"[0-9+\-*/().%\s]+", expression):
        return "表达式含非法字符，拒绝计算"
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算出错 {e}"

tools = [
    {
        "type": "function",
        "function" : {
            "name" : "calculate",
            "description" : "当用户要求做数学题时调用，计算四则表达式的值",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "expression" : {
                        "type" : "string",
                        "description" : "要计算的数学表达式，例如 '2+3*4'"
                    }
                },
                "required" : ["expression"]
            }
        }
    }
]
st.title("🤖 个人 AI 助手")
SYSTEM = "你是一个友好的个人 AI 助手，回答简洁、直接。"
HISTORY_FILE = "chat_history.json"
def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return [{"role" : "system", "content" : SYSTEM}]

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

if st.button("🗑️ 清空历史"):
    st.session_state.messages = [{"role": "system", "content": SYSTEM}]
    save_history(st.session_state.messages)
    st.rerun()

#初始化和显示历史会话
if "messages" not in st.session_state:
    st.session_state.messages = load_history()


for message in st.session_state.messages:
    if message["role"] in ("system", "tool"):
        continue
    if message.get("tool_calls"):
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("跟我说点什么..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role" : "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages,
            tools=tools,
            temperature=0.7,
            max_tokens=1024,
            stream=False,
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            st.session_state.messages.append(   #将
                {
                    "role" : "assistant",
                    "content" : msg.content,  #在这次因为想调工具，所以content为None
                    "tool_calls" : [
                        {
                            "id" : tc.id, "type" : "function", 
                            "function" : {"name" : tc.function.name, "arguments" : tc.function.arguments}
                        }
                        for tc in msg.tool_calls
                    ],
                }
            )
            for tc in msg.tool_calls:
                arg = json.loads(tc.function.arguments)     #msg里面的"tool_calls里面是json形式存在，以字符串存在，必须loads"
                if tc.function.name == "calculate":
                    result = calculate(arg["expression"])
                st.session_state.messages.append({"role" : "tool", "tool_call_id" : tc.id, "content" : result})

            response2 = client.chat.completions.create(
                model = "deepseek-chat",
                messages = st.session_state.messages,
                temperature=0.7,
                max_tokens=1024,
                stream=False,
            )
            answer = response2.choices[0].message.content
        else:
            answer = msg.content

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role" : "assistant", "content" : answer})
        save_history(st.session_state.messages)
    except Exception as e:
        st.error(f"调用失败: {e}")