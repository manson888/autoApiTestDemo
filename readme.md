框架结构
- base 基础类封装，测试用例工具
- common  公共方法封装
- conf  存放全局配置文件目录
- data  存放测试数据路径
- logs  存放测试日志目录
- report    测试报告生成目录，目前支持生成两种形式的报告
- testcase  存放测试用例文件目录
- venv  本框架使用的虚拟环境
- conftest.py 全局操作，名称是固定写法不可更改
- environment.xml allure测试报告总览-环境显示内容
- extract.yaml 接口依赖参数存放文件
- pytest.ini pytest框架规范约束，名称是固定写法不可更改
- requirements.txt 本框架所使用的到的第三方库
- run.py 主程序入口
- dockerfile与jenkinsfile自由写 不上传

- 需要用到mockserver的时候 单独运行 修改common/mockserver.py 目前这个文件只写了个支付回调的mock

- 补了一版dockerfile本地跑了一下之后 同步修改了一下依赖文档 下面是本地跑用到的命令：
- 启动 Colima （docker有点点重 我用的这个 更轻 本地够用）
colima start --cpu 2 --memory 4
-  -t 给镜像起名和版本号， . 代表当前目录
docker build -t real-pytest-project:v1 .
- --rm：运行完即删容器。-e PYTHONPATH=/app：解决 ModuleNotFoundError。-v：把容器里的报告“偷”到本地。
- docker run --rm \
  -e PYTHONPATH=/app \
  -v "$(pwd)/report:/app/report" \
  real-pytest-project:v1
- 补充一点：docker内运行 我给run里面注释掉起allure服务了 不然会弄的环境挺臃肿，因为把内容偷到了想挂载的卷（本地）所以 可以本地起服务去看结果：allure serve ./report/temp




运行截图
![](./reportPng.png)