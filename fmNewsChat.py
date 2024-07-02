import streamlit as st
from streamlit_chatbox import *
import time
import simplejson as json
import appbuilder
from appbuilder.core.console.appbuilder_client import data_class
import os

# 使用st.title()，并通过class参数指定自定义类名
st.header('凤凰FM交互式资讯知识助手')
chat_box = ChatBox()
chat_box.use_chat_name("新会话1")  # 创建一个新会话（页面加载后）


def on_chat_change():
    chat_box.use_chat_name(st.session_state["chat_name"])
    chat_box.context_to_session(
    )  # restore widget values to st.session_state when chat name changed


in_expander = False
show_history = False
# 左侧工具栏
with st.sidebar:
    st.subheader('凤凰FM交互式资讯知识助手')
    chat_name = st.selectbox("会话名称:", ["默认", "会话1"],
                             key="chat_name",
                             on_change=on_chat_change)
    chat_box.use_chat_name(chat_name)
    streaming = st.checkbox('流式输出', key="streaming", value=True)
    chat_box.context_from_session(
        exclude=["chat_name"])  # save widget values to chat context

    st.divider()

    btns = st.container()

chat_box.init_session()
chat_box.output_messages()


def on_feedback(
    feedback,
    chat_history_id: str = "",
    history_index: int = -1,
):
    reason = feedback["text"]
    score_int = chat_box.set_feedback(
        feedback=feedback,
        history_index=history_index)  # convert emoji to integer
    # do something
    st.session_state["need_rerun"] = True


feedback_kwargs = {
    "feedback_type": "thumbs",
    "optional_text_label": "wellcome to feedback",
}

if query := st.chat_input('输入您要听的资讯'):
    chat_box.user_say(query)
    chat_box.ai_say([
        Markdown("思考中...",
                 in_expander=in_expander,
                 expanded=True,
                 title="answer")
    ])
    if streaming:
        # generator = llm.chat_stream(query)
        os.environ[
            "APPBUILDER_TOKEN"] = 'bce-v3/ALTAK-JDdbJTm8UQvC6FcVmvYf3/ad840bbae22aa62ebd916d5f81d75d580d5ed00e'
        app_id = '1abd2214-1440-46f8-9968-78f6115bf5e2'  # 已发布AppBuilder应用的ID
        # 初始化智能体
        client = appbuilder.AppBuilderClient(app_id)
        # 创建会话
        conversation_id = client.create_conversation()
        message = client.run(conversation_id, query, stream=True)

        text = ""
        for content in message.content:
            text += content.answer
            chat_box.update_msg(text, element_index=0, streaming=True)
            for event in content.events:
                content_type = event.content_type
                detail = event.detail
                print(content_type)

if btns.button("清空记录"):
    chat_box.init_session(clear=True)
    st.experimental_rerun()

if show_history:
    st.write(st.session_state)
