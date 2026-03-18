# coding: utf-8
import sqlite3
import os
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), "ai_memory.db")

def init_db():
    # 连接数据库（自动创建文件）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 创建对话表（无注释，纯SQL）
    sql_conversation = """
    CREATE TABLE IF NOT EXISTS conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_question TEXT NOT NULL,
        ai_answer TEXT NOT NULL,
        keywords TEXT,
        importance INTEGER DEFAULT 1,
        create_time TEXT NOT NULL
    )
    """
    cursor.execute(sql_conversation)
    
    # 2. 创建重要性规则表（无注释，纯SQL）
    sql_rule = """
    CREATE TABLE IF NOT EXISTS importance_rule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL UNIQUE,
        level INTEGER DEFAULT 2
    )
    """
    cursor.execute(sql_rule)
    
    # 初始化默认规则（参数化查询）
    default_rules = [("Java", 3), ("Python", 3), ("AI", 3), ("区别", 2)]
    cursor.executemany(
        "INSERT OR IGNORE INTO importance_rule (keyword, level) VALUES (?, ?)",
        default_rules
    )
    
    conn.commit()
    conn.close()
    print(f"记忆库初始化成功：{DB_PATH}")

def get_importance(question: str, keywords: list) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    max_level = 1
    
    for kw in keywords:
        cursor.execute("SELECT level FROM importance_rule WHERE keyword = ?", (kw,))
        res = cursor.fetchone()
        if res:
            max_level = max(max_level, res[0])
    
    cursor.execute("SELECT COUNT(*) FROM conversation WHERE user_question = ?", (question,))
    count = cursor.fetchone()[0]
    if count >= 2:
        max_level = 3
    
    conn.close()
    return max_level

def save_conversation(question: str, answer: str, keywords: list):
    # 转义特殊字符
    question = question.replace("'", "''").replace("#", "＃")
    answer = answer.replace("'", "''").replace("#", "＃")
    keywords_str = ",".join(keywords).replace("#", "＃")
    
    importance = get_importance(question, keywords)
    create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO conversation 
        (user_question, ai_answer, keywords, importance, create_time)
        VALUES (?, ?, ?, ?, ?)
        """,
        (question, answer, keywords_str, importance, create_time)
    )
    conn.commit()
    conn.close()

def get_history(limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_question, ai_answer, create_time FROM conversation ORDER BY create_time DESC LIMIT ?",
        (limit,)
    )
    history = cursor.fetchall()
    conn.close()
    
    # 还原字符
    return [
        {
            "question": h[0].replace("＃", "#"),
            "answer": h[1].replace("＃", "#"),
            "time": h[2]
        }
        for h in history
    ]

# 初始化数据库
if __name__ == "__main__":
    init_db()