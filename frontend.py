import streamlit as st
import requests

st.title("报错助手")
st.caption("这个页面不碰 AI，所有回答都来自 localhost:8000")

if "log" not in st.session_state:
    st.session_state["log"] = []

for m in st.session_state["log"]:
    st.chat_message(m["role"]).markdown(m["content"])
    if m.get("source"):
        with st.expander("依据"):
            for s in m["source"]:
                st.write(s)

q = st.chat_input("问点什么")

if q:
    st.session_state["log"].append({"role": "user", "content": q})
    st.chat_message("user").markdown(q)

    with st.spinner("后端思考中..."):
        r = requests.get("http://127.0.0.1:8000/ask", params={"q": q})
        data = r.json()
        sources = data.get("sources", [])
    st.session_state["log"].append({"role": "assistant", "content": data["answer"],"source":sources})
    st.rerun()
