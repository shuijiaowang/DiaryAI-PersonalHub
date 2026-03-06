# 入口文件，被main.py调用
import os
import json

from server.utils.deepseekDemo import call_deepseek_chat


def initialize():
    # ========== 1. 定义所有文件路径 ==========
    input_json_path = os.path.join("server", "config", "input.json")
    diary_txt_path = os.path.join("server", "diaries", "2026-3-5.txt")
    global_info_json_path = os.path.join("server", "config", "global_info.json")
    templates_jsonc_path = os.path.join("server", "config", "templates.jsonc")
    output_jsonc_path = os.path.join("server", "config", "output.jsonc")
    # 新增：定义结果保存路径
    result_json_path = os.path.join("server", "result", "output.json")

    # ========== 2. 工具函数：读取文件原始文本（保留注释/格式） ==========
    def read_file_raw(file_path):
        """读取文件原始文本，保留所有格式和注释"""
        if not os.path.exists(file_path):
            print(f"警告：文件 {file_path} 不存在，填充为空")
            return ""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"读取文件 {file_path} 失败：{e}")
            return ""

    # ========== 3. 读取各文件内容 ==========
    global_info_content = read_file_raw(global_info_json_path)
    diary_raw_text_content = read_file_raw(diary_txt_path)
    templates_content = read_file_raw(templates_jsonc_path)
    output_content = read_file_raw(output_jsonc_path)

    # ========== 4. 读取并填充input.json ==========
    if not os.path.exists(input_json_path):
        print(f"错误：核心文件 {input_json_path} 不存在！")
        return

    # 读取input.json原始文本（修复缩进错误）
    with open(input_json_path, "r", encoding="utf-8") as f:
        input_json_raw = f.read()

    # 文本替换：将null替换为对应文件内容
    # 1. 替换global_info（JSON文件，直接插入）
    input_json_raw = input_json_raw.replace('"global_info": null', f'"global_info": {global_info_content}')
    # 2. 替换diary_raw_text（TXT文件，转义引号和换行后包裹为字符串）
    escaped_diary = diary_raw_text_content.replace('"', '\\"').replace('\n', '\\n')
    input_json_raw = input_json_raw.replace('"diary_raw_text": null', f'"diary_raw_text": "{escaped_diary}"')
    # 3. 替换templates（JSONC文件，直接插入）
    input_json_raw = input_json_raw.replace('"templates": null', f'"templates": {templates_content}')
    # 4. 替换output（JSONC文件，直接插入）
    input_json_raw = input_json_raw.replace('"output": null', f'"output": {output_content}')

    # ========== 5. 构造调用DeepSeek的消息 ==========
    user_message = f"""
请根据以下完整的 input 数据解析日记文本，生成符合要求的 output 结构化数据：
{input_json_raw}

要求：
1. 严格按照 input 中的「模板说明」和「返回结构说明」处理
2. 仅返回 output 字段的内容，无需其他多余信息
3. 保留所有注释格式，保证输出内容的可解析性
4. 输出内容必须是合法的JSON格式，避免语法错误
    """

    # 调试用：打印构造的消息（可选）
    print("=== 发送给DeepSeek的消息 ===")
    print(user_message)

    # ========== 6. 调用DeepSeek接口 ==========
    result = call_deepseek_chat(user_message=user_message)

    # ========== 7. 处理结果并保存到文件 ==========
    if result["success"]:
        print("DeepSeek 回复:", result["content"])

        # 确保result文件夹存在（不存在则创建）
        result_dir = os.path.dirname(result_json_path)
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
            print(f"创建文件夹：{result_dir}")

        # 保存AI返回结果到output.json
        try:
            # 尝试将返回内容解析为JSON并格式化保存（保证文件可读性）
            ai_content = json.loads(result["content"])
            with open(result_json_path, "w", encoding="utf-8") as f:
                json.dump(ai_content, f, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            # 如果返回内容不是JSON格式，直接保存原始文本
            with open(result_json_path, "w", encoding="utf-8") as f:
                f.write(result["content"])
        print(f"结果已保存到：{result_json_path}")
    else:
        print("调用失败:", result["error"])


# 方便单独测试该文件
if __name__ == "__main__":
    initialize()