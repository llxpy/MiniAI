# 保留原有导入
import subprocess
import json
import os
import sys
from memory_db import init_db, save_conversation, get_history
# 导入新的思考逻辑
from ai_brain import think_and_answer

# 初始化记忆库
init_db()

# 保留原有call_node_search函数（无需修改）
def call_node_search(question: str, node_script_path: str) -> dict:
    """原调用Node的函数，完整保留"""
    def get_node_exe_path():
        try:
            if os.name == "nt":
                result = subprocess.run(["where", "node"], capture_output=True, encoding="utf-8", shell=True)
            else:
                result = subprocess.run(["which", "node"], capture_output=True, encoding="utf-8")
            node_path = result.stdout.strip().split("\n")[0]
            if not node_path or not os.path.exists(node_path):
                raise Exception("Node.js路径无效")
            return node_path
        except Exception as e:
            raise Exception(f"未找到Node.js：{str(e)}")

    try:
        # 替换为你的实际Node脚本路径
        NODE_SCRIPT_PATH = r"C:\Users\Administrator\Desktop\MiniAI\node-search\search-service.js"
        if not os.path.exists(node_script_path):
            return {"success": False, "message": f"Node脚本不存在：{node_script_path}", "data": [], "keywords": []}

        node_exe = get_node_exe_path()
        safe_question = question.replace('"', '\\"').replace("'", "\\'")
        cmd = [node_exe, node_script_path, safe_question]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="ignore",
            timeout=30,
            shell=False,
            cwd=os.path.dirname(node_script_path)
        )

        if result.returncode != 0:
            error_msg = f"Node执行失败：{result.stderr[:500]}"
            return {"success": False, "message": error_msg, "data": [], "keywords": []}

        node_output = result.stdout.strip()
        if not node_output:
            return {"success": False, "message": "Node脚本无输出", "data": [], "keywords": []}

        return json.loads(node_output)
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Node执行超时", "data": [], "keywords": []}
    except json.JSONDecodeError:
        return {"success": False, "message": f"非JSON输出：{node_output[:200]}", "data": [], "keywords": []}
    except Exception as e:
        return {"success": False, "message": f"调用失败：{str(e)}", "data": [], "keywords": []}

# 核心：替换ai_answer函数
def ai_answer(question: str) -> str:
    # 你的Node脚本路径
    NODE_SCRIPT_PATH = r"C:\Users\Administrator\Desktop\MiniAI\node-search\search-service.js"
    
    # 定义搜索函数（传给思考层）
    def search_func(q):
        return call_node_search(q, NODE_SCRIPT_PATH)
    
    # 调用思考逻辑：搜索→理解→回答
    final_answer = think_and_answer(question, search_func)
    
    # 保存到记忆库
    search_res = call_node_search(question, NODE_SCRIPT_PATH)
    save_conversation(question, final_answer, search_res["keywords"])
    
    return final_answer

# 保留原有Flask代码（无需修改）
from flask import Flask, render_template, request, jsonify
app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"success": False, "answer": "请输入有效问题！"})
    
    try:
        answer = ai_answer(question)
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        return jsonify({"success": False, "answer": f"回答失败：{str(e)}"})

@app.route("/history")
def history():
    return jsonify(get_history())

if __name__ == "__main__":
    print("===== 具备「搜索-理解-反馈」能力的AI已启动 =====")
    print("访问地址：http://127.0.0.1:5000")
    print("按Ctrl+C停止服务")
    app.run(host="0.0.0.0", port=5000, debug=True)