from flask import Flask, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

# 模拟三方支付的密钥
MOCK_PRIVATE_KEY = "RSA_PRIVATE_KEY_DATA"


@app.route('/pay/gateway', methods=['POST'])
def mock_pay_gateway():
    # 1. 接收业务系统的下单请求
    data = request.json
    order_id = data.get("order_id")
    callback_url = data.get("callback_url")  # 业务系统传过来的回调地址

    print(f"收到订单: {order_id}，准备处理...")

    # 2. 立即给业务系统一个同步响应（代表三方网关接单成功）
    # 开启一个线程去处理异步回调，不阻塞主进程
    threading.Thread(target=send_async_callback, args=(order_id, callback_url)).start()

    return jsonify({"code": "00", "msg": "下单成功", "order_id": order_id})


def send_async_callback(order_id, callback_url):
    """模拟三方支付后的异步回调"""
    time.sleep(2)  # 模拟网络延迟 2 秒

    # 3. 构造回调报文（带上签名）
    payload = {
        "order_id": order_id,
        "status": "PAID",  # 模拟支付成功
        "timestamp": int(time.time()),
        "sign": "GENERATED_RSA_SIGN_HERE"  # 调用你封装的签名函数
    }

    # 4. 向你的业务系统发送回调
    try:
        requests.post(callback_url, json=payload, timeout=5)
        print(f"订单 {order_id} 回调发送成功！")
    except Exception as e:
        print(f"回调发送失败: {e}")


if __name__ == '__main__':
    app.run(port=8888)
