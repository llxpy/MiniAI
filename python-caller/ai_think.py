# MiniAI/python-caller/ai_think.py
import re
from memory_db import get_history, get_importance
import difflib

# 上下文存储（支持多轮对话）
context = {
    "last_question": "",
    "last_keywords": []
}

def intent_recognition(question: str) -> str:
    """
    意图识别：判断问题类型
    返回值：chat（闲聊）、search（事实查询）、history（历史记录）、calc（计算）、unknown（未知）
    """
    q = question.lower().strip()
    
    # 1. 闲聊意图
    chat_keywords = ["你好", "hello", "嗨", "在吗", "再见", "谢谢", "不客气", "你是谁"]
    if any(kw in q for kw in chat_keywords):
        return "chat"
    
    # 2. 历史记录意图
    history_keywords = ["历史", "记忆", "之前", "聊过", "记录"]
    if any(kw in q for kw in history_keywords):
        return "history"
    
    # 3. 计算意图
    calc_pattern = r"[0-9]+[\+\-\×\*\/][0-9]+"
    if re.search(calc_pattern, q):
        return "calc"
    
    # 4. 事实查询（默认）
    return "search"

def simple_calc(question: str) -> str:
    """简单计算推理"""
    try:
        # 替换中文符号为英文
        q = question.replace("×", "*").replace("÷", "/")
        # 提取计算式
        calc_pattern = r"([0-9]+[\+\-\*\/][0-9]+)"
        match = re.search(calc_pattern, q)
        if not match:
            return "我没看懂你要计算什么哦～"
        
        expr = match.group(1)
        # 安全计算（避免恶意代码）
        result = eval(expr, {"__builtins__": None}, {})
        return f"计算结果：{expr} = {result}"
    except:
        return "这个计算我暂时不会哦～"

def chat_response(question: str) -> str:
    """闲聊回答（基于规则推理）"""
    q = question.lower().strip()
    if "你好" in q or "hello" in q:
        return "你好呀 😊 有什么想知道的都可以问我～"
    elif "再见" in q:
        return "拜拜～下次有问题还可以来找我哦！"
    elif "谢谢" in q:
        return "不客气啦 😜"
    elif "你是谁" in q:
        return "我是你的专属AI助手，会思考、会记忆，还能帮你查资料～"
    else:
        return "哈哈，这个话题我还在学习中～换个问题问问？"

def find_similar_question(question: str, threshold: float = 0.7) -> str | None:
    """从记忆库找相似问题（推理复用历史答案）"""
    history = get_history(limit=20)  # 取最近20条对话
    if not history:
        return None
    
    # 计算相似度
    max_similarity = 0
    best_answer = None
    for h in history:
        similarity = difflib.SequenceMatcher(None, question, h["question"]).ratio()
        if similarity > max_similarity and similarity >= threshold:
            max_similarity = similarity
            best_answer = h["answer"]
    
    return best_answer

def generate_answer(question: str, search_result: dict) -> str:
    """
    核心思考逻辑：整合搜索结果/记忆/规则生成回答
    """
    # 1. 先尝试找相似历史回答
    similar_answer = find_similar_question(question)
    if similar_answer:
        return f"我之前回答过类似的问题哦：\n{similar_answer}"
    
    # 2. 无相似回答，基于搜索结果生成自然回答
    if not search_result["success"]:
        return f"抱歉，我没找到相关信息 😥：{search_result['message']}"
    
    # 提取核心信息
    keywords = search_result["keywords"]
    first_result = search_result["data"][0] if search_result["data"] else None
    
    # 3. 生成结构化回答（思考后的自然语言）
    if first_result:
        answer = f"关于「{question}」，我帮你查到这些信息：\n\n"
        answer += f"核心要点：{first_result['summary'][:150]}...\n\n"
        answer += f"更多参考：{first_result['title']}（链接：{first_result['link']}）"
    else:
        answer = f"我分析了「{question}」的关键词：{','.join(keywords)}，但暂时没找到具体信息。"
    
    # 4. 更新上下文（支持多轮对话）
    context["last_question"] = question
    context["last_keywords"] = keywords
    
    return answer

def think_and_answer(question: str, search_func) -> str:
    """
    统一思考入口：先判断意图 → 再执行对应逻辑 → 最后生成回答
    :param question: 用户问题
    :param search_func: 搜索函数（调用Node的函数）
    :return: 思考后的回答
    """
    # 1. 意图识别
    intent = intent_recognition(question)
    
    # 2. 根据意图执行逻辑
    if intent == "chat":
        answer = chat_response(question)
    elif intent == "history":
        history = get_history()
        if not history:
            answer = "我们还没有聊过哦，先来问我一个问题吧～"
        else:
            answer = "这是我们之前的对话：\n"
            for idx, h in enumerate(history[:5], 1):  # 只显示最近5条
                answer += f"{idx}. 你：{h['question']}\n   我：{h['answer'][:50]}...\n"
    elif intent == "calc":
        answer = simple_calc(question)
    elif intent == "search":
        # 先补全上下文（如用户问"它和Java的区别？"）
        if "它" in question and context["last_keywords"]:
            question = question.replace("它", context["last_keywords"][0])
        
        # 调用搜索
        search_res = search_func(question)
        # 生成思考后的回答
        answer = generate_answer(question, search_res)
    else:
        answer = "我还在学习中，暂时没理解你的问题 😂"
    
    return answer