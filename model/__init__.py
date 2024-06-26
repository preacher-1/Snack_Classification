from PIL import Image
from ultralytics import YOLO
from TestModel.models import Textdata


class Model:
    def __init__(self):
        self.model_detect_path = r'D:\djangoProject\model\pt/model_detect_sim.onnx'
        self.model_classify_path = r'D:\djangoProject\model\pt/model_cls_sim.onnx'
        self.model_detect = YOLO(self.model_detect_path, task='detect')
        self.model_classify = YOLO(self.model_classify_path, task='classify')
        self.names = (
            '中介蝮', '中华珊瑚蛇（丽纹蛇）', '中国水蛇', '孟加拉眼镜蛇', '尖吻蝮', '山烙铁头', '泰国圆斑蝰', '湖北颈槽蛇', '白唇竹叶青', '白头缅蝰', '眼镜王蛇', '短尾蝮',
            '福建华珊瑚蛇（福建丽纹蛇）', '紫沙蛇', '繁花林蛇', '红脖颈槽蛇', '舟山眼镜蛇', '菜花原矛头蝮', '虎斑颈槽蛇', '金环蛇', '铅色水蛇', '银环蛇', '黑头缅蝰',
            '（尖鳞）原矛头蝮')

    def predict(self, img: Image):
        """
        detect img
        split img
        classify img
        get data
        Args:
            img:

        Returns:
            results:    list[dict[int: (name, habitat, figure, suggestion, conf)]]
            |    |--result
            |    |    |--{id: (name, habitat, figure, suggestion, conf)}
        """
        boxes = self.detect(img)
        img_splits = self.split_image(img=img, boxes=boxes)
        top5_data = self.classify(img_splits)
        results = self.get_text(top5_data)
        return img_splits, results

    def detect(self, img: Image):
        """
        对图像进行目标检测，返回Result中的boxes
        Args:
            img:所给图像

        Returns:目标检测结果

        """
        results = self.model_detect.predict(img, device='cpu')
        boxes = results[0].boxes
        return boxes

    @staticmethod
    def split_image(img: Image, boxes):
        """
        根据目标检测结果对图像进行裁剪预处理,如果没有检测结果则直接返回原始图像
        Args:
            img:所给图像
            boxes:该图像目标检测框

        Returns:裁剪后的图像

        """
        if boxes.cls.numel():
            img_splits = []
            xyxy_list = boxes.xyxy.cpu().numpy().tolist()
            for xyxy in xyxy_list:
                img_split = img.crop(xyxy)
                img_splits.append(img_split)
            return img_splits
        else:
            return img

    def classify(self, imgs: list[Image]):
        """
        对预处理后的图片进行图像分类，返回top5,top5conf
        Args:
            imgs: 预处理后的图片

        Returns: top5_data: list[(top5, top5conf)...]

        """
        probs = []
        for img in imgs:
            results = self.model_classify.predict(img, device='cpu')
            probs.append(results[0].probs)
        top5_data = [(prob.top5, prob.top5conf.cpu().numpy().tolist()) for prob in probs]
        return top5_data

    @staticmethod
    def get_text(top5_data: list[(list, list)]):
        """
        对单个或多个子图的识别结果进行处理，返回文本信息等
        results:    list[dict[int: (name, habitat, figure, suggestion, conf)]]
        |    |--result
        |    |    |--{id: (name, habitat, figure, suggestion, conf)}
        Args:
            top5_data: 单个或多个子图的top5,top5conf
        Returns:
            results: 单个或多个子图的文本信息列表
        """
        results = []
        for top5, top5conf in top5_data:
            result = dict.fromkeys(top5, None)
            for i, idx in enumerate(top5):
                try:
                    query_result = Textdata.objects.filter(id=idx).first()
                    if query_result is None:
                        raise ValueError("No text data found for id: {}".format(idx))
                except ValueError as e:
                    print(e)
                    return None  # 返回None表示出现异常,前端显示错误信息
                else:
                    temp = (query_result.name, query_result.habitat, query_result.figure,
                            query_result.suggestion)
                    conf = round(top5conf[i], 4)
                    result[idx] = temp + (conf,)
            results.append(result)
        return results


# 初始化分类模型
yolo = Model()
