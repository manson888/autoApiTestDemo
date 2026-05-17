import allure
import pytest

from base.generateId import m_id, c_id
from base.apiutil import RequestBase
from common.readyaml import get_testcase_yaml

@allure.epic("运营管理")
@allure.feature(next(m_id) + '轮播图模块')
class TestBanner:

    @allure.story(next(c_id) + "查询首页轮播图")
    @pytest.mark.run(order=1)
    @pytest.mark.parametrize('base_info,testcase',
                             get_testcase_yaml('./testcase/BannerManager/getBannerList.yaml'))
    def test_get_banner_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
