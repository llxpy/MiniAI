import re
import json

# AI自身身份定义（核心：让AI知道“我是谁”）
AI_IDENTITY = {
    "name": "轻量级AI助手",
    "role": "帮助用户解答问题、查询信息的智能助手",
    "feature": "具备记忆功能、能搜索信息、会理解并生成个性化回答",
    "developer": "用户自定义",
    "language": "中文"
}

# 意图判断：聊天 / 计算 / 自我认知 / 通用搜索
def get_intent(question):
    q = question.strip().lower()

    # 1. 闲聊意图
    chat_words = ["你好", "嗨", "在吗", "谢谢", "再见", "拜拜"]
    for w in chat_words:
        if w in q:
            return "chat"

    # 2. 计算意图
    if re.search(r'\d+[\+\-\*/]\d+', q):
        return "calc"

    # 3. 自我认知意图（核心：识别“问AI自身”的问题）
    self_words = ["你是什么", "你是谁", "你的名字", "你能做什么", "你怎么来的", "你有什么用"]
    for w in self_words:
        if w in q:
            return "self_cognition"

    # 4. 通用搜索意图（默认）
    return "search"

# 1. 闲聊回答（基础）
def chat_answer(question):
    q = question.lower()
    if "你好" in q:
        return "你好呀！我是你的专属AI助手 😊"
    elif "谢谢" in q:
        return "不客气～能帮到你我很开心 😜"
    elif "再见" in q or "拜拜" in q:
        return "拜拜啦！有问题随时都可以来找我～"
    else:
        return "我在听呢，你继续说～"

# 2. 计算回答（基础）
def calc_answer(question):
    try:
        # 替换中文符号为英文
        safe_q = question.replace("×", "*").replace("÷", "/")
        expr = re.search(r'\d+[\+\-\*/]\d+', safe_q).group()
        # 安全计算（仅支持简单四则运算）
        ans = eval(expr, {"__builtins__": None}, {})
        return f"计算结果来啦：{expr} = {ans}"
    except:
        return "这个计算我暂时不会哦😥，换个简单点的试试？"

# 3. 核心：自我认知回答（搜索→理解→个性化生成）
def self_cognition_answer(question, search_func):
    """
    :param question: 用户问AI的问题（如“你是什么东西”）
    :param search_func: 调用Node搜索的函数
    :return: 结合搜索结果+自身身份的个性化回答
    """
    # Step 1：构造搜索关键词（AI先搜索“同类问题该怎么答”）
    search_keywords = f"{question} AI助手 标准回答"
    print(f"AI正在搜索：{search_keywords}")  # 调试用，可删除

    # Step 2：调用搜索，获取参考信息
    search_res = search_func(search_keywords)

    # Step 3：理解搜索结果，提取核心思路
    if not search_res["success"] or len(search_res["data"]) == 0:
        # 无搜索结果时，用默认身份回答
        core_answer = f"我是{AI_IDENTITY['name']}，我的主要功能是{AI_IDENTITY['feature']}。"
    else:
        # 提取搜索结果的核心摘要（理解搜索内容）
        reference_summary = search_res["data"][0]["summary"]
        # 过滤无效信息，保留核心句子
        reference_core = re.sub(r'【.*?】|（.*?）|广告|推广', '', reference_summary)
        print(f"AI理解的参考信息：{reference_core}")  # 调试用，可删除

        # Step 4：结合自身身份，生成个性化回答（核心：理解后重构）
        core_answer = f"""
我是{AI_IDENTITY['name']}，一个{AI_IDENTITY['role']}。
根据我查到的信息，对于“{question}”这个问题，通常的回答思路是：{reference_core[:200]}...
结合我的自身情况，我的回答是：我具备{AI_IDENTITY['feature']}的特点，如果你有任何问题想要解答，我都会尽力帮忙！
        """.strip()

    return core_answer

# 4. 通用搜索回答（搜索→理解→结构化反馈）
def general_search_answer(question, search_func):
    """
    通用问题的“搜索→理解→反馈”逻辑
    """
    # Step 1：执行搜索
    search_res = search_func(question)

    # Step 2：理解搜索结果
    if not search_res["success"] or len(search_res["data"]) == 0:
        return f"抱歉，我搜索了“{question}”但没有找到相关信息 😥"

    # Step 3：提取核心信息（理解内容）
    first_result = search_res["data"][0]
    # 结构化理解：标题+核心摘要+来源
    understood_info = {
        "title": first_result["title"],
        "core_summary": first_result["summary"][:200],  # 提取核心200字
        "source": first_result["link"]
    }

    # Step 4：生成“理解后”的回答（而非直接返回结果）
    final_answer = f"""
我已经搜索并理解了“{question}”的相关信息：
1. 核心结论：{understood_info['core_summary']}
2. 参考来源：{understood_info['title']}（链接：{understood_info['source']}）

以上是我整理后的核心信息，如果你想了解更多细节，可以告诉我！
    """.strip()

    return final_answer

# 统一入口：思考→行动→反馈
def think_and_answer(question, search_func):
    """
    :param question: 用户输入
    :param search_func: 调用Node搜索的函数（传入call_node_search）
    :return: 最终回答
    """
    intent = get_intent(question)

    if intent == "chat":
        return chat_answer(question)
    elif intent == "calc":
        return calc_answer(question)
    elif intent == "self_cognition":
        return self_cognition_answer(question, search_func)
    elif intent == "search":
        return general_search_answer(question, search_func)
    else:
        return "抱歉，我还没理解你的问题，能换个说法吗？"