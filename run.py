import shutil
import pytest
import os
import webbrowser
from conf.setting import REPORT_TYPE

if __name__ == '__main__':

    if REPORT_TYPE == 'allure':
        pytest.main(
            ['-s', '-v', '--alluredir=./report/temp', './testcase', '--clean-alluredir',
             '--junitxml=./report/results.xml'])

        shutil.copy('./environment.xml', './report/temp')
        # 启动allure服务
        # os.system(f'allure serve ./report/temp')

    elif REPORT_TYPE == 'tm':
        pytest.main(['-vs', '--pytest-tmreport-name=testReport.html', '--pytest-tmreport-path=./report/tmreport'])
        webbrowser.open_new_tab(os.getcwd() + '/report/tmreport/testReport.html')


#下面是用xdist分布式执行的时候用的run
#
# if __name__ == '__main__':
#
#     if REPORT_TYPE == 'allure':
#         # 添加-n 并发数设置为2
#         # 添加--dist 保正一个class里面的用例在一个进程里头运行
#         pytest.main([
#             '-s', '-v',
#             '--alluredir=./report/temp',
#             '-n', '2',
#             '--dist', 'loadscope',
#             './testcase',
#             '--clean-alluredir',
#             '--junitxml=./report/results.xml'
#         ])
#
#         # pytest.main 阻塞进程 xdist会等待所有子进程执行完毕最后执行下面进程
#         if os.path.exists('./environment.xml'):
#             shutil.copy('./environment.xml', './report/temp')
#
#         os.system(f'allure serve ./report/temp')
#
#     elif REPORT_TYPE == 'tm':
#         # 为tm方式添加进程
#         pytest.main([
#             '-vs',
#             '-n', '2',
#             '--pytest-tmreport-name=testReport.html',
#             '--pytest-tmreport-path=./report/tmreport'
#         ])
#         webbrowser.open_new_tab(os.getcwd() + '/report/tmreport/testReport.html')
