# 入口文件，被main.py调用
import os
from utils.json_utils import build_ai_prompt, get_ai_result_and_save


def initialize():
    # ========== 1. 定义所有文件路径 ==========
    input_json_path = os.path.join( "config", "input.json")
    diary_txt_path = os.path.join( "diaries", "2026-3-5.txt")
    global_info_json_path = os.path.join( "config", "global_info.json")
    templates_jsonc_path = os.path.join("config", "templates.jsonc")
    output_jsonc_path = os.path.join("config", "output.jsonc")
    result_json_path = os.path.join( "result", "output.json")

    # 2. 构造AI Prompt（调用工具函数）
    try:
        user_message = build_ai_prompt(
            input_json_path=input_json_path,
            diary_path=diary_txt_path,
            global_info_path=global_info_json_path,
            templates_path=templates_jsonc_path,
            output_path=output_jsonc_path
        )
        print("=== 发送给DeepSeek的消息 ===")
        print(user_message)
    except Exception as e:
        print(f"构造Prompt失败：{e}")
        return
    # 3. 获取AI结果并保存（调用工具函数）
    result = get_ai_result_and_save(prompt=user_message, save_path=result_json_path)
    if result["success"]:
        print(f"执行成功！结果已保存到：{result['save_path']}")
    else:
        print(f"执行失败：{result['error']}")


# 方便单独测试该文件
if __name__ == "__main__":
    initialize()
