from openai import OpenAI
from openai import APIError, APIConnectionError, AuthenticationError



def call_deepseek_chat(
        user_message: str,
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: int = 1000
) -> dict:
    """
    调用 DeepSeek Chat API 的工具函数

    参数:
        api_key: 你的 DeepSeek API Key
        user_message: 用户发送的消息内容
        model: 使用的模型名称，默认 "deepseek-chat"
        temperature: 回复随机性，0-1 之间，默认 0.7
        max_tokens: 回复的最大长度，默认 100

    返回:
        dict: 包含调用状态和结果的字典
              成功时: {"success": True, "content": 回复内容}
              失败时: {"success": False, "error": 错误信息}
    """
    # 初始化客户端
    try:
        client = OpenAI(
            api_key="sk-6f061703dc86478dbb517cf2cd5a1b2c",
            base_url="https://api.deepseek.com/v1"
        )

        # 调用 API
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_message}],
            temperature=temperature,
        )

        # 提取回复内容并返回
        reply_content = response.choices[0].message.content
        return {"success": True, "content": reply_content}

    # 捕获常见的 API 异常
    except AuthenticationError:
        return {"success": False, "error": "API Key 验证失败，请检查你的 API Key 是否正确"}
    except APIConnectionError:
        return {"success": False, "error": "无法连接到 DeepSeek 服务器，请检查网络或 API 地址"}
    except APIError:
        return {"success": False, "error": "API 调用失败，请检查请求参数或模型状态"}
    except Exception as e:
        return {"success": False, "error": f"未知错误: {str(e)}"}


# ------------------- 调用示例 -------------------
if __name__ == "__main__":
    # 替换为你的实际 API Key
    DEEPSEEK_API_KEY = "你的DEEPSEEK_API_KEY"

    # 调用函数
    result = call_deepseek_chat(
        api_key=DEEPSEEK_API_KEY,
        user_message="你好，请用一句话介绍自己",
        temperature=0.5,  # 可选参数，可根据需要调整
        max_tokens=150  # 可选参数，可根据需要调整
    )

    # 处理结果
    if result["success"]:
        print("DeepSeek 回复:", result["content"])
    else:
        print("调用失败:", result["error"])