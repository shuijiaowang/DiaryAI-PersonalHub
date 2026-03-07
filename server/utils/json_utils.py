import os
import json

from utils.ai_utils import call_deepseek_chat


def read_file_raw(file_path: str) -> str:
    """读取文件原始文本，保留所有格式和注释（通用工具）"""
    if not os.path.exists(file_path):
        print(f"警告：文件 {file_path} 不存在，填充为空")
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"读取文件 {file_path} 失败：{e}")
        return ""


def build_ai_prompt(input_json_path: str, diary_path: str, global_info_path: str, templates_path: str,
                    output_path: str) -> str:
    """构造传给DeepSeek的完整prompt（核心输入JSON处理逻辑）"""
    # 1. 读取各文件内容
    global_info_content = read_file_raw(global_info_path)
    diary_raw_text_content = read_file_raw(diary_path)
    templates_content = read_file_raw(templates_path)
    output_content = read_file_raw(output_path)

    # 2. 读取并填充input.json
    if not os.path.exists(input_json_path):
        raise FileNotFoundError(f"核心文件 {input_json_path} 不存在！")

    with open(input_json_path, "r", encoding="utf-8") as f:
        input_json_raw = f.read()

    # 文本替换：填充各字段
    input_json_raw = input_json_raw.replace('"global_info": null', f'"global_info": {global_info_content}')
    escaped_diary = diary_raw_text_content.replace('"', '\\"').replace('\n', '\\n')
    input_json_raw = input_json_raw.replace('"diary_raw_text": null', f'"diary_raw_text": "{escaped_diary}"')
    input_json_raw = input_json_raw.replace('"templates": null', f'"templates": {templates_content}')
    input_json_raw = input_json_raw.replace('"output": null', f'"output": {output_content}')

    # 3. 构造最终prompt
    user_message = f"""
请根据以下完整的 input 数据解析日记文本，生成符合要求的 output 结构化数据：
{input_json_raw}

要求：
1. 严格按照 input 中的「模板说明」和「返回结构说明」处理
2. 仅返回 output 字段的内容，无需其他多余信息
3. 保留所有注释格式，保证输出内容的可解析性
4. 输出内容必须是合法的JSON格式，避免语法错误
    """
    return user_message


def clean_ai_json_wrapper(content: str) -> str:
    """
    过滤AI返回结果中的```json```包裹符
    :param content: AI返回的原始内容
    :return: 清理后的纯文本/JSON字符串
    """
    if not content:
        return ""

    # 第一步：去除首尾空白字符（换行、空格、制表符等）
    cleaned_content = content.strip()

    # 第二步：判断并过滤```json```包裹符
    # 匹配开头的```json（允许后面跟换行/空格），结尾的```
    start_marker = "```json"
    end_marker = "```"

    if cleaned_content.startswith(start_marker) and cleaned_content.endswith(end_marker):
        # 截取开头标记后、结尾标记前的内容
        cleaned_content = cleaned_content[len(start_marker):-len(end_marker)]
        # 再次去除截取后内容的首尾空白（处理标记和JSON之间的换行/空格）
        cleaned_content = cleaned_content.strip()

    return cleaned_content


def get_ai_result_and_save(prompt: str, save_path: str) -> dict:
    """
    调用DeepSeek获取JSON结果（过滤```json```包裹），并保存到指定路径
    :param prompt: 传给AI的prompt
    :param save_path: 结果保存的JSON路径
    :return: 包含状态和结果的字典
    """
    # 1. 调用DeepSeek接口
    result = call_deepseek_chat(user_message=prompt)
    if not result["success"]:
        return {"success": False, "error": result["error"]}

    # 2. 过滤AI返回内容的```json```包裹符（核心修改点）
    raw_content = result["content"]
    cleaned_content = clean_ai_json_wrapper(raw_content)

    # 3. 处理并保存结果
    try:
        # 确保保存目录存在
        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 尝试解析为JSON并格式化保存
        ai_content = json.loads(cleaned_content)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(ai_content, f, ensure_ascii=False, indent=2)
        return {
            "success": True,
            "data": ai_content,
            "save_path": save_path,
            "raw_content": raw_content,  # 保留原始内容便于排查
            "cleaned_content": cleaned_content  # 保留清理后内容
        }

    except json.JSONDecodeError:
        # 非JSON格式则保存原始文本（已清理包裹符）
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(cleaned_content)
        return {
            "success": True,
            "data": cleaned_content,
            "save_path": save_path,
            "warning": "返回内容非JSON格式（已过滤```json```包裹符）",
            "raw_content": raw_content
        }

    except Exception as e:
        return {"success": False, "error": f"保存结果失败：{str(e)}", "raw_content": raw_content}