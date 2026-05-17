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
- dockerfile与jenkinsfile说明：jenkins yaml 和 job yaml 在编写时需要注意权限问题，如果在本地k8s环境运行时，请注意挂载路径。

- 需要使用mockserver的时候，可以修改 `common/mockserver.py`，目前文件里只写了一个支持的mock示例。

- 本项目内置了一份可以直接使用的 dockerfile。如果修改了代码，需要重新构建镜像：
- 推荐使用 Colima 作为本地 docker 环境，启动命令如下：
```bash
colima start --cpu 2 --memory 4
```

- `-t` 用于指定构建的镜像名称和版本号，`.` 代表当前目录：
```bash
docker build -t real-pytest-project:v1 .
```

- `--rm` 参数表示容器运行结束后自动删除；`-e PYTHONPATH=/app` 解决包导入找不到的问题；`-v` 将本地的 report 目录挂载到容器中：
```bash
docker run --rm \
  -e PYTHONPATH=/app \
  -v "$(pwd)/report:/app/report" \
  real-pytest-project:v1
```

- 提示：在 docker 中运行结束后，由于使用了 `-v` 挂载，测试报告会直接生成在你本地电脑的 `report/temp` 目录下。你无需进入容器，直接在本地运行以下命令即可查看测试报告：
```bash
allure serve ./report/temp
```

- 提示： split_yapi.py 可用于接大模型 生成用例 替换配置区域即可

![](./reportPng.png)