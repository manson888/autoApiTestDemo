import allure
import pytest

from base.generateId import m_id, c_id
from base.apiutil import RequestBase
from common.readyaml import get_testcase_yaml


@allure.feature(next(m_id) + '存款模块')
class TestCashing:

    @allure.story(next(c_id) + "获取存款通道列表")
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase',
                             get_testcase_yaml('./testcase/CashInManager/getCashInChannelList.yaml'))
    def test_get_channel_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '发起卡转卡')
    @pytest.mark.run(order=2)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/CashInManager/CashinChannel.yaml'))
    def test_per_cashing(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + '提交订单')
    @pytest.mark.run(order=3)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml('./testcase/CashInManager/SubmitCash.yaml'))
    def test_submit_cashing(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
