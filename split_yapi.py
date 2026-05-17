import json
import os
import re
import openai
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==================== 配置区域 ====================
API_KEY = "你的_API_KEY"
BASE_URL = "https://deepseek.com"  # 或者是你正在使用的 AI 官方/代理地址
MODEL_NAME = "deepseek-chat"  # 模型名称，如 deepseek-chat, gpt-4o 等

YAPI_JSON_FILE = "yapi_all_interfaces.json"  # 你的 YApi 全量大 JSON 文件路径
OUTPUT_BASE_DIR = "testcase"  # 你的用例输出根目录

# 线程池并发大小：推荐 5-10。注意根据你购买的大模型账号的 RPM (每分钟请求数限制) 来调整
MAX_WORKERS = 8
# =================================================

client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)


def translate_categories_by_ai(chinese_names):
    """【串行执行】让 AI 一次性把所有中文分类名翻译成规范的英文模块名"""
    prompt = f"""
你是一个精通自动化测试框架架构的专家。
我有一个测试框架目录，现在需要将以下 YApi 的中文接口分类名称，转换成符合 Python 文件夹命名规范的英文模块名（推荐使用大驼峰命名法，如 UserManager, OrderManagement, FinanceBilling）。

【待翻译的中文分类列表】：
{json.dumps(chinese_names, ensure_ascii=False, indent=2)}

【严格输出格式要求】：
请必须且只能返回一个标准的 JSON 键值对字符串，不要包含 ```json 这样的 Markdown 标记。格式如下：
{{
  "中文分类名1": "TranslatedEnglishName1",
  "中文分类名2": "TranslatedEnglishName2"
}}
"""
    print("🤖 正在请求 AI 批量翻译中文模块名为英文规范...")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw_content = response.choices.message.content.strip()
    if raw_content.startswith("```"):
        raw_content = re.sub(r"^```[a-zA-Z]*\n", "", raw_content)
        raw_content = re.sub(r"\n```$", "", raw_content)

    return json.loads(raw_content)


def generate_case_by_ai(interface_json, module_name):
    """【核心调用】让 AI 同时生成符合项目规范的 .py 代码和 .yaml 数据"""
    prompt = f"""
Role: 你是一个精通 pytest + allure，且完全理解我当前项目底层框架规范的顶级测试开发专家。

Task: 请根据我提供的【YApi 定义】，参考我当前的【数据驱动框架规范】，为我生成高标准的自动化测试用例。生成内容必须包含一个执行文件 (.py) 和一个数据文件 (.yaml)，并放到指定的 testcase 模块目录下。

【框架及生成规范】：
1. 架构规范：我不使用在 py 文件中写原生 requests 和 assert 断言的方式，而是严格遵循“执行逻辑与数据分离”的机制：
   - .py 文件仅用于参数化加载 yaml 数据并执行：`RequestBase().specification_yaml(base_info, testcase)`
   - 必须使用 @pytest.mark.parametrize 和 get_testcase_yaml()

2. 文件要求：
   - 需生成在 testcase/{module_name}/ 目录下。
   - .py 文件：类名和方法名需语义化，包含 allure.epic, allure.feature, allure.story`，且直接使用模板中 `next(m_id) 和 next(c_id) 的写法。
   - .yaml 文件：严格遵循 - baseInfo 和 testCase 的层级结构。

3. YAML 细节规范：
   - header 必须携带标准通用参数：
     pmtoken: ${{get_extract_data(pmtoken)}}
     device: '1'
   - validation (断言) 必须使用我底层 common/assertions.py 支持的语法（如 eq, contains 等），禁止写不支持的 schema 断言。
   - 用例覆盖：除了正常成功的用例外，必须自动根据接口入参或业务逻辑设计至少 1-2 个异常或边界（健壮性）用例。

【当前接口信息】：
模块目录：{module_name}
YApi 定义：
{json.dumps(interface_json, ensure_ascii=False, indent=2)}

【输出格式要求】：
为了方便我的脚本解析，请必须且只能返回一个标准的 JSON 字符串，格式如下（不要包含 ```json 这样的 Markdown 标记）：
{{
  "py_code": "这里填生成的整个 .py 文件的纯文本内容，注意换行符使用 \\n",
  "yaml_code": "这里填生成的整个 .yaml 文件的纯文本内容，注意换行符使用 \\n"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    raw_content = response.choices.message.content.strip()
    if raw_content.startswith("```"):
        raw_content = re.sub(r"^```[a-zA-Z]*\n", "", raw_content)
        raw_content = re.sub(r"\n```$", "", raw_content)

    return json.loads(raw_content)


def worker_task(interface, module_name):
    """每个线程独立执行的单个接口生成任务"""
    title = interface.get("title", "unknown_api")
    path_raw = interface.get("path", "").strip("/")
    method = interface.get("method", "GET").lower()

    # 过滤路径里的特殊字符，确保文件名合法
    clean_path = re.sub(r'[^a-zA-Z0-9_]', '_', path_raw)
    file_prefix = f"{clean_path}_{method}"

    target_dir = os.path.join(OUTPUT_BASE_DIR, module_name)
    os.makedirs(target_dir, exist_ok=True)

    py_file_path = os.path.join(target_dir, f"test_{file_prefix}.py")
    yaml_file_path = os.path.join(target_dir, f"{file_prefix}.yaml")

    # 幂等校验：避免覆盖已有文件
    if os.path.exists(py_file_path) or os.path.exists(yaml_file_path):
        return f"⚠️  跳过：【{title}】的用例已存在。"

    try:
        # 调用大模型生成
        ai_output = generate_case_by_ai(interface, module_name)

        # 写入物理文件
        with open(py_file_path, "w", encoding="utf-8") as py_f:
            py_f.write(ai_output["py_code"])

        with open(yaml_file_path, "w", encoding="utf-8") as yaml_f:
            yaml_f.write(ai_output["yaml_code"])

        return f"✅ 成功生成：【{title}】 -> test_{file_prefix}.py & .yaml"
    except Exception as e:
        return f"❌ 失败：【{title}】生成出错，原因: {e}"


def main():
    if not os.path.exists(YAPI_JSON_FILE):
        print(f"❌ 错误：在当前目录下未找到 YApi 全量文件 {YAPI_JSON_FILE}")
        return

    with open(YAPI_JSON_FILE, "r", encoding="utf-8") as f:
        yapi_data = json.load(f)

    # 1. 提取所有好分类的中文名字
    chinese_categories = [cat.get("name") for cat in yapi_data if cat.get("name")]

    # 2. 借助 AI 拿到中文到英文的映射字典（串行一次性完成）
    try:
        translation_map = translate_categories_by_ai(chinese_categories)
        print("💡 模块名翻译映射成功：")
        print(json.dumps(translation_map, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ 翻译模块名失败，原因: {e}。将降级使用拼音或默认名称。")
        translation_map = {name: f"Module_{i}" for i, name in enumerate(chinese_categories)}

    # 3. 展开所有接口，放入多线程任务队列中
    tasks = []
    for category in yapi_data:
        cat_chinese_name = category.get("name", "DefaultModule").replace(" ", "")
        module_name = translation_map.get(cat_chinese_name, cat_chinese_name)
        interfaces = category.get("list", [])

        for interface in interfaces:
            # 将每个接口数据和它所属的英文模块目录打包成任务
            tasks.append((interface, module_name))

    print(f"\n🚀 任务收集完毕，共计 {len(tasks)} 个接口。开始开启 {MAX_WORKERS} 个线程高并发调用 AI...")

    # 4. 开启线程池并发执行大模型请求
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交所有任务到线程池
        future_to_interface = {
            executor.submit(worker_task, task[0], task[1]): task[0] for task in tasks
        }

        # 实时监听并打印每个线程返回的生成结果
        for future in as_completed(future_to_interface):
            result_message = future.result()
            print(result_message)

    print("\n🎉 所有并发任务处理完毕！请前往项目根目录下的 'testcase/' 文件夹查看生成的代码和数据。")


if __name__ == "__main__":
    main()
