# doc-qa

上传自己的文档，向它提问，答案只来自文档，找不到就说不知道。

## 解决什么问题

公司制度、个人笔记这类内容网上搜不到、模型也没学过，直接问它会编。
这个工具让你上传文件后提问，回答有出处，没有依据就承认不知道。

## 怎么用

1. `pip install -r requirements.txt`
2. `uvicorn server:app --reload`（后端，端口 8000）
3. `streamlit run frontend.py`（前端）

## 架构

```
Streamlit 前端 → FastAPI /ask → 向量检索 → qwen → SQLite 记录
```

- 前端只管界面，不碰 AI
- 后端负责检索、拼接资料、调用模型
- 文档切块后转成向量，提问时算余弦相似度取最相关三段
- 问答记录存 SQLite，`/history` 可查

## 遇到的坑

- 检索永远返回三条，哪怕一条都不相关 → 加相对阈值过滤
- `CREATE TABLE IF NOT EXISTS` 不会更新已有表结构 → 只能重建
- Streamlit 每次交互重跑整个脚本，画在屏幕上的东西会被冲掉 → 先存 session_state
