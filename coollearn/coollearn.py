import streamlit as st
from dotenv import load_dotenv
from .common import (
    generate_plan_outline,
    write_stream,
    get_coollearn_prompt,
    stream_chat,
    get_option_index,
    sync_plan_data,
    load_plan_data_by_topic,
    get_plan_list,
    reset_plan,
    message_to_markdown,
    init_streamlit_config,
)
from datetime import datetime
import json
import os

load_dotenv()


def main():
    # 学习深度、学习风格、语气风格、推理框架定义
    depth_options = ["小学", "初中", "高中", "大学", "研究生"]
    style_options = ["教科书", "纪录片", "费曼式", "苏格拉底式", "讲故事"]
    tone_options = ["鼓励性", "中立性", "信息性", "友好性", "幽默性"]
    framework_options = ["演绎法", "归纳法", "类比法", "因果法"]
    model_options = ["GLM-3-Turbo", "GLM-4"]

    st.set_page_config(page_title="酷学-CoolLearn", page_icon="📚")

    init_streamlit_config()

    hide_margin_css = """
        <style>
        .css-18e3th9 {
            padding-top: 0rem;
        }
        /* 或者根据 Streamlit 的具体版本和 CSS 类名进行调整 */
        </style>
        """

    # 将自定义 CSS 应用到 Streamlit 应用中
    st.markdown(hide_margin_css, unsafe_allow_html=True)

    if "coollearn_model" not in st.session_state:
        st.session_state.coollearn_model = "GLM-4"

    if "coollearn_llm_apikey" not in st.session_state:
        st.session_state.coollearn_llm_apikey = ""

    if "coollearn_topic" not in st.session_state:
        st.session_state.coollearn_topic = "李白的浪漫主义诗歌与其生平"

    if "coollearn_depth" not in st.session_state:
        st.session_state.coollearn_depth = "初中"

    if "coollearn_style" not in st.session_state:
        st.session_state.coollearn_style = "教科书"

    if "coollearn_tone" not in st.session_state:
        st.session_state.coollearn_tone = "友好性"

    if "coollearn_framework" not in st.session_state:
        st.session_state.coollearn_framework = "演绎法"

    if "plan_outline" not in st.session_state:
        st.session_state.plan_outline = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.title("酷学")
        tab0, tab1, tab2 = st.tabs(["学习计划", "学习偏好", "设置"])

        with tab0:
            st.session_state.coollearn_topic = st.text_input(
                "学习主题",
                st.session_state.coollearn_topic,
                placeholder="比如，李白的浪漫主义诗歌与其生平",
            )
            history_plan = st.selectbox("历史学习计划", ["..."] + get_plan_list())
            if history_plan != "...":
                if st.button("加载学习计划"):
                    load_plan_data_by_topic(history_plan)
            else:
                if st.button("重置学习计划"):
                    reset_plan()
                    st.rerun()
            st.download_button(
                label=f"导出学习记录",
                data=message_to_markdown(
                    st.session_state.coollearn_topic, st.session_state.messages
                ).encode("utf-8"),
                file_name=f"{st.session_state.coollearn_topic}-学习记录.md",
            )

            st.image(
                os.path.join(os.path.dirname(__file__), "coollearn.png"),
                use_column_width=True,
            )
            st.caption("酷学是您的个性化学习好帮手， 但酷学也会出错哦😯")

        with tab1:
            st.session_state.coollearn_depth = st.selectbox(
                "学习深度",
                depth_options,
                index=get_option_index(depth_options, st.session_state.coollearn_depth),
            )
            st.session_state.coollearn_style = st.selectbox(
                "学习风格",
                style_options,
                index=get_option_index(style_options, st.session_state.coollearn_style),
            )
            st.session_state.coollearn_tone = st.selectbox(
                "语气风格",
                tone_options,
                index=get_option_index(tone_options, st.session_state.coollearn_tone),
            )
            st.session_state.coollearn_framework = st.selectbox(
                "推理框架",
                framework_options,
                index=get_option_index(
                    framework_options, st.session_state.coollearn_framework
                ),
            )

        with tab2:
            st.session_state.coollearn_model = st.selectbox(
                "GLM 模型",
                model_options,
                index=get_option_index(model_options, st.session_state.coollearn_model),
            )
            llm_apikey = st.text_input("API Key", type="password")
            if llm_apikey:
                st.session_state.coollearn_llm_apikey = llm_apikey
            st.caption(
                """API Key 是您的私有密钥， 请不要泄露给他人。
    如果你希望持久使用密钥， 可以设置 GLM_APIKEY 环境变量。
    您可以从 https://open.bigmodel.cn/ 获取您自己的 apikey"""
            )

    with st.expander("学习计划", expanded=True):
        col1, col2 = st.columns([1, 1])
        plan_act = col1.button("创建学习计划")
        plan_outline_box = st.empty()
        if plan_act:
            if "coollearn_topic" not in st.session_state:
                st.error("学习主题不能为空！")
                st.stop()

            try:
                st.session_state.messages = []
                _response = generate_plan_outline(
                    st.session_state.coollearn_topic,
                    st.session_state.coollearn_depth,
                    st.session_state.coollearn_style,
                    st.session_state.coollearn_tone,
                    st.session_state.coollearn_framework,
                )
                plan_outline = write_stream(plan_outline_box, _response)
                if plan_outline:
                    st.session_state.plan_outline = (
                        plan_outline
                        + f"\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    sync_plan_data()
            except json.JSONDecodeError:
                st.error("生成学习计划失败, 请重试！")

        if st.session_state.plan_outline:
            plan_outline_box.markdown(st.session_state.plan_outline)
            col2.download_button(
                label=f"下载学习计划",
                data=st.session_state.plan_outline.encode("utf-8"),
                file_name=f"{st.session_state.coollearn_topic}-plan.txt",
            )

    if not st.session_state.plan_outline:
        st.warning("请创建学习计划！")
        st.stop()

    if prompt := st.chat_input(placeholder="请输入"):
        st.session_state.messages.append({"role": "user", "content": prompt})

    if not st.session_state.messages:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "欢迎使用酷学！如果您已经创建好学习计划，请说 `开始` 来开始对话。请记住，虽然您可以通过快捷按钮来推进学习进度， 但您仍然可以随时提出各种问题，并且可能获得意外的收获。",
            }
        )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if (
        st.session_state.messages
        and st.session_state.messages[-1]["role"] != "assistant"
    ):
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                placeholder = st.empty()
                sysmsg = get_coollearn_prompt(
                    st.session_state.coollearn_depth,
                    st.session_state.coollearn_style,
                    st.session_state.coollearn_tone,
                    st.session_state.coollearn_framework,
                    st.session_state.plan_outline,
                )
                chat_prompt = st.session_state.messages[-1]["content"]
                response = stream_chat(
                    sysmsg,
                    chat_prompt,
                    st.session_state.messages,
                    temperature=0.7,
                    model=st.session_state.coollearn_model,
                )
                full_response = write_stream(placeholder, response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

    if st.session_state.messages:
        sync_plan_data()

    st.empty()
    st.empty()
    st.divider()
    actions_placeholder = st.empty()
    cols = actions_placeholder.columns([1, 1, 1, 1, 1, 1, 1])
    actions = ["开始", "继续", "测试", "详情", "思考", "导图", "评估"]

    for index in range(len(actions)):
        if cols[index].button(actions[index]):
            if actions[index] == "评估":
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": f"本次评估截止时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    }
                )
            st.session_state.messages.append(
                {"role": "user", "content": actions[index]}
            )
            actions_placeholder.empty()
            st.rerun()


if __name__ == "__main__":
    main()
