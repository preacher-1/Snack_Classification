import threading

import requests
from requests.exceptions import RequestException
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import time


class myYOLO(YOLO):
    # 处理URL，获取图片并进行预测
    def process_url(self, url):
        # 处理URL，获取图片并进行预测
        try:
            # 发送GET请求获取图片数据
            response = requests.get(url)
            response.raise_for_status()  # 检查响应是否成功
        except RequestException as e:
            # 捕获请求异常
            print("请求图片失败:", e)
            return None  # 返回None表示出现异常
        # 解析图片数据
        try:
            # 读取图片数据
            image_data = BytesIO(response.content)
            # 使用Pillow库打开图片
            img = Image.open(image_data)
            # return img  # 返回图片对象
        except Exception as e:
            # 捕获其他异常，比如图片数据无效等
            print("处理图片失败:", e)
            return None  # 返回None表示出现异常
        # 调用模型预测
        return super().predict(img)

    # 返回有关文本信息，待实现
    def process_flag(self, flag):
        pass


def test_yolo(i):
    print(i)
    results = yolo.predict(r"C:\Users\liuyu\Desktop\1.png")
    print(i,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),end=" ")
    print(results[0].names[0])


# 初始化分类模型
yolo = myYOLO('./ultralytics-main/ultralytics/cfg/models/v8/yolov8m-cls.pt')
# th = threading.Thread(target=test_yolo,args=(1,), daemon=True)  # 异步加载模型
# th.start()
# th.join()
threadings = []
for i in range(10):
    # print(i)
    time.sleep(0.5)
    th = threading.Thread(target=test_yolo,args=(i,), daemon=True)  # 异步加载模型
    threadings.append(th)
    th.start()

for th in threadings:
    th.join()
time.sleep(10)
# results = yolo.predict(r"C:\Users\liuyu\Desktop\1111.png")[0]


'''
result 
|    |--names = {dict:1000}
|    |--probs
|    |--data = {Tensor:(1000,)}
|        |--top1 = {int}
|        |--top1conf = {Tensor:()}
|        |--top5 = {list:5}
|        |--top5conf = {Tensor:(5,)}
|    |--speed
|    |--orig_img
|    |--orig_shape
|    |--path
'''
