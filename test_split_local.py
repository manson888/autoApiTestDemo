import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 测试配置 ====================
YAPI_JSON_FILE = "yapi_all_interfaces.json"  # 第一步创建的小 JSON
OUTPUT_BASE_DIR = "testcase"
MAX_WORKERS = 2  # 测试并发


# =================================================

def mock_translate_categories_by_ai(chinese_names):
    """【模拟 AI 翻译】离线模拟大模型的翻译返回"""
    print("🤖 (Mock AI) 正在模拟翻译中文模块名为英文规范...")
    # 建立一个本地硬编码的翻译字典
    mock_map = {
        "用户管理": "UserManager",
        "订单中心": "OrderManagement"
    }
    # 如果遇到没定义的，就兜底用大写字母加数字
    return {name: mock_map.get(name, f"Module_{i}") for i, name in enumerate(chinese_names)}


def mock_generate_case_by_ai(interface_json, module_name):
    """【模拟 AI 生成】离线模拟大模型返回符合你数据驱动规范的代码包裹"""
    title = interface_json.get("title", "未知接口")
    path = interface_json.get("path", "/api")
    method = interface_json.get("method", "GET")

    # 动态计算出文件名，用于 yaml 参数化时的加载
    clean_path = re.sub(r'[^a-zA-Z0-9_]', '_', path.strip("/"))
    file_prefix = f"{clean_path}_{method.lower()}"

    # 1. 模拟动态生成的 .py 文本内容（已完美修改为你的真实引用路径和 id 迭代器写法）
    mock_py_code = f"""import allure
import pytest

from base.generateId import m_id, c_id
from base.apiutil import RequestBase
from common.readyaml import get_testcase_yaml

@allure.epic("{module_name}模块")
@allure.feature("{title}")
class Test{module_name}:

    @allure.story("{title}自动化用例")
    @pytest.mark.parametrize("base_info, testcase", get_testcase_yaml("testcase/{module_name}/{file_prefix}.yaml"))
    def test_{file_prefix}(self, base_info, testcase):
        # 使用你规范中的 next(m_id) 和 next(c_id) 写法（这里仅做示例，AI在真实生成时会根据你的需要进行拼装）
        # m = next(m_id)
        # c = next(c_id)
        RequestBase().specification_yaml(base_info, testcase)
"""

    # 2. 模拟动态生成的 .yaml 数据文本
    mock_yaml_code = f"""- baseInfo:
    request_name: {title}-正向成功
    url: {path}
    method: {method}
    headers:
      Content-Type: application/json
      pmtoken: ${{get_extract_data(pmtoken)}}
      device: '1'
  testCase:
    - case_name: {title}成功场景
      body: {{}}
      validation:
        - eq: [status_code, 200]
        - contains: [message, "success"]

- baseInfo:
    request_name: {title}-异常边界
    url: {path}
    method: {method}
    headers:
      Content-Type: application/json
      pmtoken: ${{get_extract_data(pmtoken)}}
      device: '1'
  testCase:
    - case_name: {title}缺失通用参数场景
      body: {{}}
      validation:
        - eq: [status_code, 400]
"""

    return {
        "py_code": mock_py_code,
        "yaml_code": mock_yaml_code
    }


def worker_task(interface, module_name):
    """每个线程独立执行的单个接口物理落地任务"""
    title = interface.get("title", "unknown_api")
    path_raw = interface.get("path", "").strip("/")
    method = interface.get("method", "GET").lower()

    clean_path = re.sub(r'[^a-zA-Z0-9_]', '_', path_raw)
    file_prefix = f"{clean_path}_{method}"

    target_dir = os.path.join(OUTPUT_BASE_DIR, module_name)
    os.makedirs(target_dir, exist_ok=True)

    py_file_path = os.path.join(target_dir, f"test_{file_prefix}.py")
    yaml_file_path = os.path.join(target_dir, f"{file_prefix}.yaml")

    if os.path.exists(py_file_path) or os.path.exists(yaml_file_path):
        return f"⚠️  跳过：【{title}】的用例已存在。"

    try:
        # 离线模拟调用
        ai_output = mock_generate_case_by_ai(interface, module_name)

        # 物理写盘
        with open(py_file_path, "w", encoding="utf-8") as py_f:
            py_f.write(ai_output["py_code"])

        with open(yaml_file_path, "w", encoding="utf-8") as yaml_f:
            yaml_f.write(ai_output["yaml_code"])

        return f"✅ 成功生成：【{title}】 -> test_{file_prefix}.py & .yaml"
    except Exception as e:
        return f"❌ 失败：【{title}】生成出错，原因: {e}"


def main():
    if not os.path.exists(YAPI_JSON_FILE):
        print(f"❌ 错误：在当前目录下未找到 YApi 测试小文件 {YAPI_JSON_FILE}")
        return

    with open(YAPI_JSON_FILE, "r", encoding="utf-8") as f:
        yapi_data = json.load(f)

    # 1. 提取中文名
    chinese_categories = [cat.get("name") for cat in yapi_data if cat.get("name")]

    # 2. 模拟翻译
    translation_map = mock_translate_categories_by_ai(chinese_categories)

    # 3. 收集多线程任务
    tasks = []
    for category in yapi_data:
        cat_chinese_name = category.get("name", "DefaultModule").replace(" ", "")
        module_name = translation_map.get(cat_chinese_name, cat_chinese_name)
        interfaces = category.get("list", [])

        for interface in interfaces:
            tasks.append((interface, module_name))

    print(f"\n🚀 开始通过多线程（并发度:{MAX_WORKERS}）进行物理文件本地落地测试...")

    # 4. 多线程并发写盘
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_interface = {
            executor.submit(worker_task, task[0], task[1]): task for task in tasks
        }
        for future in as_completed(future_to_interface):
            print(future.result())

    print("\n🎉 离线模拟验证完毕！请检查项目根目录下的 'testcase/' 文件夹。")


if __name__ == "__main__":
    main()
