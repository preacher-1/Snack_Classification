import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

import os
from model import yolo
import base64
from PIL import Image
from io import BytesIO
import datetime
import time


# from model import yolo


# Create your views here.

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def preprocess(request):
    if is_ajax(request=request) and request.method == 'POST':
        file = request.FILES.get('data')
        if file:
            try:
                # 读取文件内容
                file_content = file.read()
                # 将文件内容转换为PIL的Image对象
                image = Image.open(BytesIO(file_content))
                # 验证图片的格式
                image.verify()  # 如果不是有效的图片，这里会抛出异常

                save_path = os.path.join(settings.BASE_DIR, 'upload_temp_images')  # 确定保存图片的路径
                if not os.path.exists(save_path):
                    os.makedirs(save_path)  # 如果保存路径不存在，则创建该文件夹
                file_path = os.path.join(save_path,
                                         f'{file.name.split(".")[0]}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.jpeg')  # 确定图片的具体保存路径
                # 保存图片到本地
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                # image.save(file_path, 'JPEG')
                return JsonResponse({'stat': 'preprocess_complete', 'img_path': file_path})
            except Exception as e:
                print(e)
                return JsonResponse({'stat': 'failed', 'error': f'无法处理上传文件: {str(e)}'})
    return render(request, 'main.html')


# 处理URL，获取图片并进行预测
def download_image(request):
    max_size = 1024 * 1024 * 10  # 10MB
    timeout = 10
    try:
        # 记录用时
        start = time.time()
        url = request.POST.get('data')
        if url.startswith('http') is False:
            url = 'https://' + url
        # 发送GET请求获取图片数据
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        response.raise_for_status()  # 检查响应是否成功

        # 检查内容类型
        content_type = response.headers.get('Content-Type')
        if not content_type or 'image' not in content_type:
            return JsonResponse(
                {'stat': 'failed', 'error': f'URL不指向图片文件, content type: {content_type}'})
        # image = Image.open(BytesIO(response.content))

        # 检查文件大小
        image_size = int(response.headers.get('Content-Length')) / 1024  # 单位KB
        image_size = round(image_size, 2)
        if image_size and image_size > max_size:
            return JsonResponse({'stat': 'failed', 'error': '图片大小超过限制'})

        save_path = os.path.join(settings.BASE_DIR, 'upload_temp_images')  # 确定保存图片的路径
        if not os.path.exists(save_path):
            os.makedirs(save_path)  # 如果保存路径不存在，则创建该文件夹
        file_path = os.path.join(save_path,
                                 f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.jpeg')  # 确定图片的具体保存路径
        # 保存图片到本地
        with open(file_path, 'wb') as f:
            f.write(response.content)

        return JsonResponse({
            'stat': 'download_complete',
            'img_path': file_path,
            'size': image_size,
            'used_time': f'{time.time() - start:.2f}'
        })
    except requests.Timeout:
        return JsonResponse({'stat': 'failed', 'error': '下载图片超时，请重试'})
    except requests.TooManyRedirects:
        return JsonResponse({'stat': 'failed', 'error': '重定向过多，无法下载图片'})
    except requests.RequestException as e:
        return JsonResponse({'stat': 'failed', 'error': f'网络错误: {str(e)}'})
    except OSError as e:
        return JsonResponse({'stat': 'failed', 'error': f'本地保存失败: {str(e)}'})
    except Exception as e:
        return JsonResponse({'stat': 'failed', 'error': f'下载失败：{str(e)}'})


def process(request):
    if is_ajax(request=request) and request.method == 'POST':
        b64strs, results = [], None
        try:
            # 读取上一阶段保存本地的图片文件
            path = request.POST.get('path')
            image = Image.open(path)
            # 得到图片处理结果
            img_splits, results = yolo.predict(image)

            # 原始图片base64编码
            for img in img_splits:
                buffered = BytesIO()
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue())
                b64strs.append(f'data:image/jpeg;base64,{img_str.decode("utf-8")}')

            # 立即销毁本地图片
            image.close()
            os.remove(path)

            # 处理结果返回前端
            if results is None:
                return JsonResponse({'stat': 'error', 'error': '图片处理过程中出现错误，请截取屏幕并反馈给工作人员。'})
            return JsonResponse(
                {'stat': 'completed', 'orig_images': b64strs, 'results': results})
        except NotImplementedError as e:
            # 本地图片删除失败，记录日志并通知人工介入
            print(e)
            if results is None:
                return JsonResponse({'stat': 'error', 'error': '图片处理过程中出现错误，请截取屏幕并反馈给工作人员。'})
            return JsonResponse(
                {'stat': 'completed', 'orig_images': b64strs, 'results': results})
        except Exception as e:
            return JsonResponse({'stat': 'failed', 'error': str(e)})
    return JsonResponse({'stat': 'failed', 'error': '非法请求'})
