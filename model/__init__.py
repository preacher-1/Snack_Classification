import requests
from requests.exceptions import RequestException
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
from TestModel.models import Textdata


class myYOLO(YOLO):
    """
        result
        |    |--names = {dict:1000}
        |    |--probs
        |        |--data = {Tensor:(1000,)}
        |        |--top1 = {int}
        |        |--top1conf = {Tensor:()}
        |        |--top5 = {list:5}
        |        |--top5conf = {Tensor:(5,)}
        |    |--speed
        |    |--orig_img
        |    |--orig_shape
        |    |--path
    """

    def __init__(self, model_path):
        super().__init__(model_path)
        # self.result = None

    def predict(self, *args):
        pass

    # 处理URL，获取图片并进行预测
    def process_url(self, url):
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
            response
            return None  # 返回None表示出现异常
        # 调用模型预测
        self.result = super().predict(img)
        # return self.result

    # 图片预处理，待实现
    def process_image(self, img):
        pass

    # 与数据库交互，返回有关文本信息，待实现
    def process_flag(self):
        top5 = self.result.probs.top5
        top5conf = self.result.probs.top5conf
        # names = [self.result.names[i] for i in top5]

        # 待实现：与数据库交互，返回有关文本信息
        pass


class Model():
    def __init__(self):
        pass
        # self.yolo_det = myYOLO('')
        # self.yolo_cls = myYOLO('/ultralytics-main/ultralytics/cfg/models/v8/yolov8m-cls.pt')

    def predict(self, img):
        pass

    def detect(self, img):
        pass

    def split_image(self, img):
        pass

    def classify(self, img):
        pass

    def get_text(self, top5, top5conf):
        results = dict.fromkeys(top5, None)
        for idx in top5:
            query_result = Textdata.objects.filter(id=idx)
            if query_result is None:
                raise ValueError("No text data found for id: {}".format(idx))
            else:
                temp = [query_result[0].name, query_result[0].habitat, query_result[0].figure,
                        query_result[0].suggestion, query_result[0].img_path]
                results[idx] = temp
        return results


# 初始化分类模型
yolo = myYOLO('/ultralytics-main/ultralytics/cfg/models/v8/yolov8m-cls.pt')
# yolo = YOLO(r'D:\djangoProject\model\ultralytics-main\ultralytics\cfg\models\v8\yolov8m-cls.pt')
