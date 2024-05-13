from django.shortcuts import render
import base64
import threading
import time
from model import yolo

# Create your views here.


# def hello(request):
#     return HttpResponse("Hello world ! ")


# def runoob(request):
#     context = {'hello': 'Hello World!'}
#     return render(request, 'runoob.html', context)
#
#
# def runoob2(request):
#     views_name = "菜鸟教程"
#     return render(request, "runoob.html", {"name": views_name})



def search_post(request):
    """
    return
        --results[5]
            --each result
                --image example
                --strs
                    --snake class
                    --acc
                    --area
                    --figures
                    --tips
    """
    # if request.method == 'POST':
    #     queue.append(request.POST)

    if request.method == 'POST':
        ctx = {'img':None, 'textmessage':None}  # 要返回给html的字典，包含预留记号的对应内容
        file, url, text = None, None, 'example'
        url = request.POST.get('url')
        file = request.FILES.get('file')
        pic = None

        if file:
            pic = yolo.predict(file.read())
        elif url:
            pic = yolo.process_url(url)

        if pic is not None:
            b64str = base64.b64encode(pic).decode('utf-8')  # pic
            ctx['img'] = f'<img src="data:image/jpeg;base64,{b64str}" width = "300">'
        else:
            ctx['img'] = 'No image found'
        ctx['textmessage'] = text

        return render(request, "search.html", ctx)

    else:
        print('GET ')
        return render(request, "search.html")


def process(request):
    ctx = {'img': None, 'textmessage': None}  # 要返回给html的字典，包含预留记号的对应内容
    file, url, text = None, None, 'example'
    url = request.POST.get('url')
    file = request.FILES.get('file')
    pic = None

    if file:
        pic = yolo.predict(file.read())
    elif url:
        pic = yolo.process_url(url)

    if pic is not None:
        b64str = base64.b64encode(pic).decode('utf-8')  # pic
        ctx['img'] = f'<img src="data:image/jpeg;base64,{b64str}" width = "300">'
    else:
        ctx['img'] = 'No image found'
    ctx['textmessage'] = text
