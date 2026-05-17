# -*- coding: utf-8 -*-
import time

import pytest


from common.readyaml import ReadYamlData
from base.removefile import remove_file
from common.dingRobot import send_dd_msg
from common.tlgRobot import send_telegram_message
#from common.Pjenkins import PJenkins
from conf.setting import dd_msg, tl_msg

import warnings

yfd = ReadYamlData()
import os

def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption(
        "--env", action="store", default="dev", help="运行环境：dev(测试服) 或 prod(线上服)"
    )

@pytest.fixture(scope="session", autouse=True)
def set_env(request):
    """获取环境变量并写入系统变量中，供全局读取"""
    env = request.config.getoption("--env")
    os.environ["TEST_ENV"] = env  # 存入 os 环境变量



@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)

    yfd.clear_yaml_data()
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])


def generate_test_summary(terminalreporter):
    """生成测试结果摘要字符串"""
    total = terminalreporter._numcollected
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    # 尝试获取开始时间
    # 在新版 pytest 中，可以通过 _session_start 获取，如果是 Instant 对象则取其 timestamp
    session_start = getattr(terminalreporter, '_session_start', time.time())

    # 如果 session_start 是 pytest 8.0+ 的 Instant 对象，需要特殊处理
    if hasattr(session_start, 'timestamp'):
        duration = time.time() - session_start.timestamp()
    elif isinstance(session_start, float):
        duration = time.time() - session_start
    else:
        # 如果实在获取不到，给个默认值 0，避免程序崩溃
        duration = 0


    # 部署到jkins里面才能用 不然会抱错 拿生成的报告地址用的
    #pjkins = PJenkins()
    #report = pjkins.report_success_or_fail()

    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """
    #点击查看测试报告：{report}
    print(summary)
    return summary


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    summary = generate_test_summary(terminalreporter)
    if dd_msg:
        send_dd_msg(summary)
    elif tl_msg:
        send_telegram_message(summary)
