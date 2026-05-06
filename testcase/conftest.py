import pytest
import allure
from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from common.recordlog import logs
from common.readyaml import ReadYamlData
from common.connection import ConnectMysql

"""
-function：每一个函数或方法都会调用
-class：每一个类调用一次，一个类中可以有多个方法
-module：每一个.py文件调用一次，该文件内又有多个function和class
-session：是多个文件调用一次，可以跨.py文件调用，每个.py文件就是module,整个会话只会运行一次
-autouse：默认为false，不会自动执行，需要手动调用，为true可以自动执行，不需要调用
- yield：前置、后置
"""


@pytest.fixture(autouse=True)
def start_test_and_end():
    logs.info('-------------接口测试开始--------------')
    yield
    logs.info('-------------接口测试结束--------------')


@pytest.fixture(scope='session', autouse=True)
@allure.story("登录")
def system_login():
    try:
        # api_info = get_testcase_yaml('./data/loginName.yaml')
        api_info = get_testcase_yaml('./data/loginDev.yaml')
        RequestBase().specification_yaml(api_info[0][0], api_info[0][1])
    except Exception as e:
        logs.error(f'登录接口出现异常，导致后续接口无法继续运行，请检查程序！，{e}')
        exit()


@pytest.fixture(scope='session', autouse=True)
def datadb_init():
    """
    后置处理器，比如测试之后的数据清理
    数据库可以预先预置一批本次测试的数据，在测试完成之后将这批数据清理，就不会对系统造成影响，也不会产生脏数据
    :return:
    """
    # conn = ConnectMysql()
    # yield
    # sql = "delete from sys_user where login_name='test999'"
    # conn.delete(sql)
    # allure.attach('将测试数据清空', 'fixture后置', allure.attachment_type.TEXT)

    pass

@pytest.fixture(scope='session', autouse=True)
def clear_extact_data():
    ReadYamlData().clear_yaml_data()



def pytest_runtest_makereport(item, call):
    """
    利用 pytest-rerunfailures 的钩子，动态修改重试延迟
    """
    # 确保只处理打标记了 flaky 的用例
    marker = item.get_closest_marker("flaky")
    if marker:
        # 获取当前已经运行过的次数（初次运行是 1，第一次重试是 2...）
        # 这是 pytest-rerunfailures 内部注入到 item 对象的属性
        execution_count = getattr(item, "execution_count", 0)

        if execution_count > 0:
            # 策略：动态计算延迟时长（例如：前三次 60s，之后每次增加 120s）
            if execution_count <= 3:
                new_delay = 60
            else:
                new_delay = 60 + (execution_count - 3) * 120

            # 关键一步：动态覆盖装饰器中的 reruns_delay
            marker.kwargs["reruns_delay"] = new_delay

            # 打印到控制台，方便调试
            print(f"\n[动态策略] 用例 {item.name} 第 {execution_count} 次失败，下次重试延迟: {new_delay}s")

# 下面是在用例中的示例代码
# import pytest
# import allure
# import requests
#
#
# @allure.feature("动态退避重试示例")
# @pytest.mark.flaky(reruns=10, reruns_delay=10)  # 这里的10s会被钩子函数动态修改
# def test_async_api_dynamic(order_id):
#     with allure.step("检查接口 B 状态"):
#         res = requests.get(f"https://example.com{order_id}")
#         status = res.json().get("status")
#
#         allure.attach(f"当前状态: {status}", "状态跟踪")
#         assert status == "SUCCESS", "订单处理中，等待重试..."
