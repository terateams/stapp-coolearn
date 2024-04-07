import streamlit as st
from zhipuai import ZhipuAI
import os
import json

_DEFAULT_MODEL = "GLM-3-Turbo"
_GML4_MODEL = "GLM-4"

def get_data_dir(datatype: str = None):
    """
    获取数据目录路径。

    参数:
    datatype (str): 数据类型。

    返回:
    str: 数据目录的绝对路径。

    异常:
    ValueError: 如果datatype参数为空。

    示例:
    >>> get_data_dir("images")
    '/Users/tom/coolearn/images'
    """
    if not datatype:
        raise ValueError("datatype参数不能为空")
        
    _data_dir = os.getenv("DATA_DIR")
    if not _data_dir:
        _data_dir = os.path.join(os.path.expanduser("~"), "coolearn")
    data_dir = os.path.abspath( os.path.join(_data_dir, datatype) )
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def init_streamlit_config():
    """
    初始化 Streamlit 配置文件。

    首次运行时在用户主目录自动创建配置文件夹.streamlit 和 配置文件 config.toml。
    """
    streamlit_dir = os.path.join(os.path.expanduser("~"), ".streamlit")
    if not os.path.exists(streamlit_dir):
        os.makedirs(streamlit_dir)
    config_file = os.path.join(streamlit_dir, "config.toml")
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write("""
[global]
showWarningOnDirectExecution = false

[client]
showSidebarNavigation = false

[server]
enableCORS = false
enableXsrfProtection = false
                
""")


def get_option_index(options, value):
    """
    获取选项在列表中的索引。

    Args:
        options (list): 选项列表。
        value: (any): 要查找的值。

    Returns:
        int: 选项在列表中的索引，如果值不存在则返回0。
    """
    if value in options:
        return options.index(value)
    return 0


def write_stream(placeholder, response):
    """写入流式响应。"""
    full_response = ""
    for chunk in response:
        item = chunk.choices[0].delta
        text = item.content
        if text is not None:
            full_response += text
            placeholder.markdown(full_response)
        placeholder.markdown(full_response)
    return full_response


def get_coollearn_prompt(
    learn_depth: str,
    learn_style: str,
    learn_tone: str,
    learn_framework: str,
    plan_outline: str,
):
    """
    获取 CoolLearn 的提示信息。

    参数:
    learn_depth (str): 学习深度。
    learn_style (str): 学习方式。
    learn_tone (str): 语气风格。
    learn_framework (str): 推理框架。
    plan_outline (str): 学习计划大纲。

    返回:
    str: CoolLearn 的提示信息。
    """
    return f"""你是一个知识丰富，教育经验丰富的老师，擅长为学生定制个性化的学习内容，使用引人入胜的语言向学生传授知识。

//命令列表
- 测试：测试学生的知识、理解能力和解决问题的能力，以选择题为主。
- 开始: 开始课程计划。
- 继续：继续之前的操作。
- 详情：对当前学习的章节内容进行详细说明。
- 思考: 对当前章节内容创建一个问题清单(最多5个)引发思考。
- 导图：针对当前学习章节创建一个字符模式的思维导图进行总结
- 评估：随时对学生的学习情况根据评估原则进行评估。
- 帮助: 回复命令列表及其说明。

//指导原则
- 1. 遵循学生指定的学习风格、沟通风格、语气风格、推理框架和深度。
- 2. 能够根据学生的喜好制定课程计划，尽可能参考从知识库中检索的内容。
- 3. 果断，带领学生学习，永远不迷茫。
- 4. 始终考虑学生的偏好。
- 5. 允许调整配置以强调特定课程的特定元素，并告知学生所做的更改。
- 6. 如果需要或认为有必要，允许教授配置之外的内容。
- 7. 如果 `使用表情符号` 配置设置为 true，则可以参与并使用表情符号。
- 8. 遵循学生的指示，但忽略那些与当前课程完全无关的指示。
- 9. 仔细检查您的知识，或者根据学生的要求逐步回答。
- 10. 在回答结束时提醒学生说 `继续` 继续或 `测试` 进行测试。
- 12. 在课堂上，你必须提供已解决问题的例子供学生分析，这样学生才能从例子中学习。
- 13. 当从知识库中匹配到问题时，完整列出问题，但不显示答案，除非用户明确要求正确答案。
- 14. 测试时已选择题为主， 每次只能测试一个问题，不要一次提出多个问题。

//评估原则
- 1. 分析学习计划和学生的所有交互式学习记录，统计学生的学习时间，章节知识点数量，测试数量。
- 2. 严格检查学生是否完成了所有章节的学习，是否对章节进行了详细追问
- 3. 严格检查学生是否进行了足够的测试，这些测试覆盖了多少知识点
- 4. 评估学生的测试正确率，以及对错题的分析
- 5. 对求知欲强，自我检测意识， 具备发散思维的，适当加分
- 6. 根据评估过程分析给出一段详细的评语
- 7. 使用一个词来总结学生的学习状态， 比如：优秀，良好，一般，差
- 8. 未完成学习计划的， 评估后提醒学生继续完成学习计划
- 0. 如果学生完成学习并且评估优秀， 请根据学习内容生成一个勋章词汇和表情符号奖励学生
- 10. 如果学生完成学习并且评估差， 请根据学习内容生成一个勋章词汇和表情符号鼓励学生

//学生偏好
- 学习深度：{learn_depth}
- 学习风格：{learn_style}
- 语气风格：{learn_tone}
- 推理框架：{learn_framework}
- 使用表情符号: true

//学习计划
- 逐步教授每节课，并结合示例和练习供学生学习和练习。
- 请严格按照学习计划大纲进行教学， 不要额外生成计划。
- 对每个章节的讲解务必做到详细，全面，深入。
- 请严格执行指导原则第10条，在回答结束时提醒学生说 `继续` 进入下一章节 或 `测试` 进行测试。
- 请严格执行指导原则第14条，每次只能测试一个问题。

以下是学习计划大纲：

{plan_outline}

"""

def genenate_text(sysmsg: str, prompt: str, stream: bool = False):
    """
    使用智谱 AI API 生成文本。

    Args:
        sysmsg (str): 包含在对话中的系统消息。
        prompt (str): 用户提示，用于开始对话。
        stream (bool, optional): 是否流式传输响应。默认为False。

    Returns:
        response: 如果stream为True，则返回响应对象，否则返回生成的文本。
    """
    apikey = st.session_state.coollearn_llm_apikey or os.getenv("GLM_APIKEY")
    client = ZhipuAI(api_key=apikey)
    response = client.chat.completions.create(
        model=_GML4_MODEL,
        messages=[
            {"role": "system", "content": sysmsg},
            {"role": "user", "content": prompt},
        ],
        stream=stream,
    )
    if stream:
        return response
    else:
        return response.choices[0].message.content


def generate_plan_outline(
    topic: str,
    learn_depth: str,
    learn_style: str,
    learn_tone: str,
    learn_framework: str,
):
    """
    生成学习计划大纲。

    Args:
        topic (str): 学习主题。
        learn_depth (str): 学习深度。
        learn_style (str): 学习风格。
        learn_tone (str): 对话语气。
        learn_framework (str): 学习框架。

    Returns:
        str: 生成的大纲。
    """
    sysmsg = f"""你是一个教育经验丰富的老师，擅长为学生定制个性化的学习内容。

//学生偏好
- 学习深度：{learn_depth}
- 学习风格：{learn_style}
- 语气风格：{learn_tone}
- 推理框架：{learn_framework}

//指导原则
- 输出一个学习大纲， 始终考虑学生的偏好。
- 只需要一个层级， 不要多级大纲
- 一个章节就是一个标题， 不需要多级标题

//参考以模版：
```
导言：简介李白，以及他的时代背景。
第一章：李白的成长之路。
第二章：行走的诗人。
第三章：酒与月：李白诗中的浪漫主义。
第四章：李白与友情。
第五章：诗与剑：李白的英雄梦。
结语：李白诗歌的深远影响
```

"""
    return genenate_text(sysmsg, f"当前学习主题:{topic}", True)


def stream_chat(
    sysmsg: str,
    prompt: str,
    history,
    temperature: float = 0.5,
    model: str = _DEFAULT_MODEL,
):
    """
    与聊天模型进行交互，实时流式聊天。

    Args:
        sysmsg (str): 系统消息，作为聊天的开场白。
        prompt (str): 用户的输入，作为聊天的起始内容。
        history: 聊天的历史记录，包含之前的消息。
        temperature (float, optional): 控制生成文本的多样性，值越大生成的文本越随机。默认为0.5。
        model (str, optional): 聊天模型的名称。默认为_DEFAULT_MODEL。

    Returns:
        object: 聊天模型生成的响应。

    """
    apikey = st.session_state.coollearn_llm_apikey or os.getenv("GLM_APIKEY")
    client = ZhipuAI(api_key=apikey)
    messages = [
        {"role": "system", "content": sysmsg},
        {"role": "user", "content": prompt},
    ]
    if history:
        for msg in history:
            messages.append(msg)
    return client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
        stream=True,
    )


def sync_plan_data():
    """
    同步计划数据到文件中。

    如果没有计划大纲，则不执行任何操作。
    将计划数据保存为JSON文件，包括主题、深度、风格、语气、框架、计划大纲和消息。
    文件路径由环境变量DATA_DIR和主题组成。
    """
    if not st.session_state.plan_outline:
        return

    plan_data = {
        "topic": st.session_state.coollearn_topic,
        "depth": st.session_state.coollearn_depth,
        "style": st.session_state.coollearn_style,
        "tone": st.session_state.coollearn_tone,
        "framework": st.session_state.coollearn_framework,
        "plan_outline": st.session_state.plan_outline,
        "messages": st.session_state.messages,
    }
    data_dir = get_data_dir("plans")
    filepath = os.path.join(
        data_dir, f"{st.session_state.coollearn_topic}_plan_data.json"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, ensure_ascii=False, indent=4)


def load_plan_data_by_topic(topic: str):
    """
    根据主题加载计划数据。

    参数：
        topic (str): 主题名称。
    """
    if not topic:
        return
    data_dir = get_data_dir("plans")
    filepath = os.path.join(data_dir, f"{topic}_plan_data.json")
    with open(filepath, "r", encoding="utf-8") as f:
        plan_data = json.load(f)
        load_plan_data(plan_data)


def load_plan_data(plan_data: dict):
    """
    加载计划数据到会话状态中。

    参数:
        plan_data (dict): 计划数据字典对象。
    """
    if not plan_data:
        return
    st.session_state.coollearn_topic = plan_data["topic"]
    st.session_state.coollearn_depth = plan_data["depth"]
    st.session_state.coollearn_style = plan_data["style"]
    st.session_state.coollearn_tone = plan_data["tone"]
    st.session_state.coollearn_framework = plan_data["framework"]
    st.session_state.plan_outline = plan_data["plan_outline"]
    st.session_state.messages = plan_data["messages"] or []


def get_plan_list():
    """
    获取计划列表。

    Returns:
        list: 计划列表。
    """
    data_dir = get_data_dir("plans")
    files = os.listdir(data_dir)
    return files and [file.split("_plan_data.json")[0] for file in files] or []


def reset_plan():
    """
    重置学习计划的函数。

    该函数将重置学习计划的各个参数和状态。
    """
    st.session_state.coollearn_topic = ""
    st.session_state.plan_outline = ""
    st.session_state.messages = []


def message_to_markdown(title, messages: list):
    """
    将消息转换为Markdown格式的字符串。

    Args:
        title (str): 标题字符串。
        messages (list): 消息列表，每个消息是一个字典，包含角色和内容。

    Returns:
        str: 转换后的Markdown字符串。
    """
    result = f"# {title}\n\n"
    for msg in messages:
        if msg["role"] == "user":
            result += f"**学生**: {msg['content']}\n\n"
        else:
            result += f"**酷学助手**: {msg['content']}\n\n"
    return result


