import io
import sys
from typing import Optional, Dict, Any


class PythonExecutor:
    def __init__(self):
        # 这是我们的“沙盒”命名空间，代码产生的变量都会存在这里
        self.global_scope = {
            "__builtins__": __builtins__,  # 允许使用基础内置函数 (如 print, len)
            # 你可以在这里预注入一些工具给 AI 用
            # "helper_tool": my_helper_function
        }

    def execute(self, code: str, return_var_name: Optional[str] = None) -> Dict[str, Any]:
        """
        执行代码并返回结果

        Args:
            code: 要执行的 Python 代码字符串
            return_var_name: 如果你想获取代码中某个变量的值，传变量名

        Returns:
            包含状态、输出、返回值的字典
        """
        # 1. 准备捕获 print 输出
        old_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        result = {
            "status": "success",
            "print_output": "",
            "return_value": None,
            "error": None,
            "error_traceback": ""
        }
        try:
            # 执行代码，所有变量写入 self.global_scope
            exec(code, self.global_scope)

            # 3. 如果指定了要获取的变量名，从 scope 里取出来
            if return_var_name:
                if return_var_name in self.global_scope:
                    result["return_value"] = self.global_scope[return_var_name]
                else:
                    result["status"] = "warning"
                    result["error"] = f"变量 '{return_var_name}' 未在代码中定义"

        except Exception as e:
            result["status"] = "error"
            result["error"] = f"{type(e).__name__}: {str(e)}"
            # 可以在这里把 traceback 也打出来方便调试
            import traceback
            result["error_traceback"] = traceback.format_exc()

        finally:
            # 4. 恢复标准输出，保存捕获到的内容
            sys.stdout = old_stdout
            result["print_output"] = captured_output.getvalue()

        return result


#  executor=PythonExecutor()
#     #注意返回结果的换行？顶格？
#     code1 = """
# print("Hello, PythonExecutor!")
# a = 10 + 20
#         """
#     result1 = executor.execute(result["content"],return_var_name="a")
#     print("=== 示例 1 结果 ===")
#     print(f"状态: {result1['status']}")
#     print(f"打印输出: {repr(result1['print_output'])}")  # repr 能显示换行符
#     print(f"返回值: {result1['return_value']}")
#     print()