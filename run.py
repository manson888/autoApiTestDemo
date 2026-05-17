import shutil
import pytest
import os
import webbrowser
# 引入新增的配置项
from conf.setting import REPORT_TYPE, USE_XDIST, XDIST_WORKERS

if __name__ == '__main__':
    # 在这里指定你想运行的环境，想跑线上就改成 "prod"
    ENV = "dev"
    
    # 基础运行参数，追加自定义的 --env 
    pytest_args = ['-s', '-v', f'--env={ENV}']
    
    # 动态判断是否追加分布式参数
    if USE_XDIST:
        # 添加-n 并发数 
        # 添加--dist 保正一个class里面的用例在一个进程里头运行
        pytest_args.extend(['-n', str(XDIST_WORKERS), '--dist', 'loadscope'])

    if REPORT_TYPE == 'allure':
        # 追加 allure 相关参数
        pytest_args.extend([
            '--alluredir=./report/temp',
            './testcase',
            '--clean-alluredir',
            '--junitxml=./report/results.xml'
        ])
        
        # 执行 pytest
        pytest.main(pytest_args)

        # pytest.main 阻塞进程 xdist会等待所有子进程执行完毕最后执行下面进程
        if os.path.exists('./environment.xml'):
            shutil.copy('./environment.xml', './report/temp')

        # 启动 allure 服务
        os.system(f'allure serve ./report/temp')

    elif REPORT_TYPE == 'tm':
        # 追加 tm 相关参数
        pytest_args.extend([
            '--pytest-tmreport-name=testReport.html',
            '--pytest-tmreport-path=./report/tmreport'
        ])
        
        # 执行 pytest
        pytest.main(pytest_args)
        webbrowser.open_new_tab(os.getcwd() + '/report/tmreport/testReport.html')
