from .forms import LoginForm
from django.http import HttpResponse
from django.http import JsonResponse
from .forms import VehicleForm
from .forms import SmokeForm
from .models import Image

from collections import defaultdict
from django.conf import settings

import os
import cv2
from ultralytics import YOLO
import base64
import numpy as np
from bs4 import BeautifulSoup
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from .forms import RegistrationForm
from django.contrib.auth.models import User


# Create your views here.

def user(request):
    # 获取当前已登录的用户信息
    current_user = request.user
    # 获取用户的头像、用户名和密码信息
    avatar = current_user.profile.avatar.url if hasattr(current_user, 'profile') and current_user.profile.avatar else None
    username = current_user.username
    password = '*' * 10  # 这里仅为示例，实际情况下应该使用更安全的方法来保护用户密码信息

    current_user = request.user  # 假设这里是从请求中获取当前用户
    image_records = Image.objects.filter(user=current_user)

    context = {
        'avatar': avatar,
        'username': username,
        'password': password,
    }
    return render(request, 'user.html', context)


# def update_images(request):
#     current_user = request.user
#     # 从 Image 模型中获取当前用户的图片信息
#     image_records = Image.objects.filter(user=current_user)
#
#     # 构造包含图片信息的字典列表
#     images_data = [{'id': image.id, 'name': image.name} for image in image_records]
#
#     # 返回 JSON 响应
#     return JsonResponse(images_data, safe=False)


def login_in(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # 登录成功后的操作
                return redirect('index')
            else:
                # 处理登录失败的情况
                return render(request, 'login.html', {'form': form, 'error_message': '用户名或密码不正确'})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # 处理验证通过的表单数据，例如保存到数据库等
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            # 进行后续处理，比如创建用户对象并保存到数据库
            # 创建用户对象
            user = User.objects.create_user(username=username, password=password)
            # 其他需要保存的用户信息也可以在这里设置，比如 user.email = form.cleaned_data['email']

            # 保存用户信息到数据库
            user.save()
            # 在这里添加你的逻辑代码
            return redirect('login')  # 注册成功后重定向到登录页面
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def index(request):
    return render(request, 'index.html')


def parse_images_from_url(url):
    try:
        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'cookie':'SESSIONID=eJiOztPhagzsxGBvveLb82ovlNfneGyzAF1UaOERJTP; JOID=UVoWC0w8mE8ehycyLDc9mGynQMc5HrpnMqAFEAQbum02qwAQDrKfFHOCJzgoxR-VymreY90ZFEX7QxJ2TdVqVpE=; osd=Vl8QAk87nUkXhCA3Kj4-n2mhScQ-G7xuMacAFg0YvWgwogMXC7SWF3SHITErwhqTw2nZZtsQF0L-RRt1StBsX5I=; YD00517437729195%3AWM_TID=0LYPxRcseR1FEUAUQFeVNfK1bhGXMzxz; YD00517437729195%3AWM_NI=vEg8Wg2mLO9s%2FSq4zD%2BgGejQpXBFwYa6LEcTmjMXPiSKcL%2B2Jr7k4M37S2amyMS%2BFDJR34y4wMJeJM34tpLhjxHDiRfMmvPQpXAtqLCuL3fyr4B9d9Mnq6lWWFcpcgo8SU4%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6ee87f96faa87ad8ced33b0b88ab2c45a828b8f83d43a95bfb692f75daa8bfd92f12af0fea7c3b92ab69ba9d9d66df2b384b0bc79ed8dbfd5f950e9b98986e95bb4888ea7f653a3ea84a6e260afb683b9d3639195adadaa3a8aaef98cb747f1e99dd3e467bb939dccc5508a8efdd5fc40b5938686c947f1ecbc91cf64aaa888a5ec5aa693a397d35bb4888f95f44881ab84d4e573b2ec8edae7338fb2bfd7ef5d959aad91e26dade89db6b737e2a3; _zap=630d118a-82d0-4e60-b8e5-7389586b6a98; d_c0=AUCX_mJi6RePTqN0Lvqo0-96kyNcT50a6C8=|1703579148; __snaker__id=LK5vwGsURZP32elO; q_c1=92ffe0a19e574a6098aae495f48c3e76|1706257109000|1706257109000; tst=r; _xsrf=pZxC41YRH865OwQIHkyzSZ7AFeG8WRvS; __zse_ck=001_ub3AcU4ojeTIwf8iOFVZq0KiPyRcWLUaJIACsqVAgH/D5ixGY7gzg2DxoMswljJCGJ4xuWwwfXoCjsyqtT5Ksp/Eim5mB6eRElXj=/4100SVPoidD5g/SX6QfRD6MVOl; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1716612391,1717124830,1717504579,1717505178; z_c0=2|1:0|10:1717505370|4:z_c0|80:MS4xbDJGa0hRQUFBQUFtQUFBQVlBSlZUVnBiVEdkakxkWGJXMmx0THFaSXNCR1FTejRUUFhEdF9BPT0=|47210f4e3a924e769563485f411ce2d58bfadd882e5c230fdacde4da7ffbe6e7; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1717505422; BEC=4da77e64be3cf762e3831e43ab259290; KLBRSID=c450def82e5863a200934bb67541d696|1717505422|1717505175',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # print(soup.prettify())
            image_urls = []

            # 通过标签名和属性来定位图片元素
            figure_tags = soup.find_all('figure')
            # 遍历每个 figure 元素
            for figure in figure_tags:
                img_tag = figure.find('img')
                # 提取图片的 src 属性值
                if img_tag:
                    image_url = img_tag.get('src')
                    if image_url:
                        # 如果图片链接是相对路径，则拼接为绝对路径
                        if not image_url.startswith('http'):
                            image_url = url + image_url
                        # 去掉查询参数部分
                        if '?' in image_url:
                            image_url_without_query = image_url.split('?')[0]
                        else:
                            image_url_without_query = image_url
                        image_urls.append(image_url_without_query)
                # 如果在 figure 中没有找到图片，则遍历每个带有 align="center" 属性的 <p> 元素
            if not image_urls:
                center_paragraphs = soup.find_all('p')
                for paragraph in center_paragraphs:
                    img_tag = paragraph.find('img')
                    if img_tag:
                        image_url = img_tag.get('src')
                        if image_url:
                            # 如果图片链接是相对路径，则拼接为绝对路径
                            if not image_url.startswith('http'):
                                image_url = url + image_url
                            # 去掉查询参数部分
                            if '?' in image_url:
                                image_url_without_query = image_url.split('?')[0]
                            else:
                                image_url_without_query = image_url
                            image_urls.append(image_url_without_query)
            return image_urls
        else:
            print("Failed to fetch URL:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred while parsing images from URL:", str(e))
        return None


def examine_url(request):
    if request.method == 'POST':
        # 获取表单数据
        url = request.POST.get('url')

        # 发送网络请求获取网页内容
        response = requests.get(url)
        if response.status_code == 200:
            # 解析网页内容，提取图像URL
            image_urls = parse_images_from_url(url)
            if image_urls:
                all_results = []

                for image_url in image_urls:
                    # 下载图片
                    image_name = image_url.split('/')[-1]
                    # # 创建 Smoke 对象并保存到数据库
                    # smoke_instance = Smoke.objects.create()
                    # # 构建图片保存的路径
                    # image_path = dynamic_path2(smoke_instance, image_name)
                    # # 保存图片信息到 Smoke 实例
                    # smoke_instance.images = image_path
                    # smoke_instance.save()

                    # 构建图片保存的路径
                    image_folder_path = os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', 'examine', image_name)
                    os.makedirs(image_folder_path, exist_ok=True)  # 创建文件夹，如果已经存在则不会报错

                    # 构建图片保存的完整路径
                    image_path = os.path.join(image_folder_path, image_name)
                    # 写入图片
                    with open(image_path, 'wb') as f:
                        f.write(requests.get(image_url).content)

                    # 调用识别函数并保存识别结果图片
                    image_base64, label = get_smoke2(image_path)
                    output_name = "output_" + image_name
                    original_img_path = '/media' + '/vehicle/' + 'images/' + 'examine/' + image_name + '/' + image_name
                    output_img_path = '/media' + '/vehicle/' + 'images/' + 'examine/' + image_name + '/' + output_name
                    all_results.append({'original': original_img_path, 'output': output_img_path, 'label': label})

                return render(request, 'examine.html', {'all_results': all_results})
            else:
                return HttpResponse("No images found on the webpage.")
        else:
            return HttpResponse("Failed to fetch URL:", response.status_code)
    else:
        form = SmokeForm()
        return render(request, '111.html', {'form': form})


def get_smoke2(img_path):
    model = YOLO(r"D:\yolov5\django-yolov8-main\vsmoke\best.pt")  # 加载自定义模型权重
    img_name = os.path.basename(img_path)
    img = cv2.imread(img_path)
    results = model.predict(img_path)

    label_colors = {
        "smoke": (0, 0, 255),  # 红色
        "no_smoke": (0, 255, 0),  # 绿色
    }

    type = "No Detected"  # 初始化type变量

    # 处理检测结果并在图片上绘制边界框和标签
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            x1, y1, x2, y2 = result.boxes.xyxy[i].tolist()
            cls = result.boxes.cls[i]
            conf = result.boxes.conf[i]
            type = model.names[int(cls)]
            color = label_colors.get(type)
            # label = f"{model.names[int(cls)]} {conf:.2f}"
            # print(label)
            if type:
                label = f"{model.names[int(cls)]} {conf:.2f}"
            else:
                label = "No Detected"

            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(img, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    output = "output_" + img_name
    # 将识别结果保存为output.png
    cv2.imwrite(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', 'examine', img_name, output), img)

    # 返回识别结果图片
    retval, buffer = cv2.imencode('.jpg', img)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64, type


def examine_batch_photo(request):
    if request.method == 'POST':
        form = SmokeForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('images')
            # print(files)
            all_results = []

            for file in files:
                name = file.name.replace(' ', '')
                # print(name)
                # obj = form.save(commit=False)
                # obj.images.name = name
                # obj.save()
                obj = form.save(commit=False)
                obj.images = file
                obj.save()

                file_path = os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', 'examine', name, name)
                # 调用识别函数并保存识别结果图片
                image_base64, label = get_smoke(file_path)
                print(label)

                output = "output_" + name
                original_img_path = '/media' + '/vehicle/' + 'images/' + 'examine/' + name + '/' + name
                output_img_path = '/media' + '/vehicle/' + 'images/' + 'examine/' + name + '/' + output

                all_results.append({'original': original_img_path, 'output': output_img_path, 'label': label})

            # 保存所有对象
            form.save()

            return render(request, 'examine.html', {'form': form, 'all_results': all_results})
    else:
        form = SmokeForm()

    return render(request, 'examine.html', {'form': form})


"smoke"


def get_smoke(img_path):
    model = YOLO(r"D:\yolov5\django-yolov8-main\vsmoke\best.pt")  # 加载自定义模型权重
    img_name = os.path.basename(img_path)
    img = cv2.imread(img_path)
    results = model.predict(img_path)

    label_colors = {
        "smoke": (0, 0, 255),  # 红色
        "no_smoke": (0, 255, 0),  # 绿色
    }

    type = "No Detected"  # 初始化type变量

    # 处理检测结果并在图片上绘制边界框和标签
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            x1, y1, x2, y2 = result.boxes.xyxy[i].tolist()
            cls = result.boxes.cls[i]
            conf = result.boxes.conf[i]
            type = model.names[int(cls)]
            color = label_colors.get(type)
            # label = f"{model.names[int(cls)]} {conf:.2f}"
            # print(label)
            if type:
                label = f"{model.names[int(cls)]} {conf:.2f}"
            else:
                label = "No Detected"

            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(img, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    output = "output_" + img_name
    # 将识别结果保存为output.png
    cv2.imwrite(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', 'examine', img_name, output), img)

    # 返回识别结果图片
    retval, buffer = cv2.imencode('.jpg', img)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64, type


# try视图
def try_(request):
    form = VehicleForm()
    # 检查用户提交的方法是否是POST请求
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        name = request.FILES['file'].name
        # print(name)
        # 如果是图片文件
        if 'image/' in request.FILES['file'].content_type:
            # if form.is_valid():
            #     obj = form.save(commit=False)
            #     obj.file.name = name  # 将原始文件名赋值给 obj.file.name
            #     # print(obj.file.name)
            #     obj.save()
            # else:
            #     form.save()

            if form.is_valid():
                if ' ' in name:
                    name = name.replace(' ', '')
                # if '(' in name:
                #     name = name.replace('(', '').replace(')', '')
                    obj = form.save(commit=False)
                    obj.file.name = name
                    obj.save()
                else:
                    form.save()
                form = VehicleForm()
                # 实例化一个表单

                # path of saved input image
                # "crops" 用于存放裁剪后的车辆图像，"plates" 用于存放识别出的车牌图像
                path = os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', name, name)
                try:
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', name, "crops"))
                    os.mkdir(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', name, "plates"))
                except OSError:
                    pass
                # 调用get_class
                crops, labels, img, filenames = get_class(path)
                plates = []
                # platestxt = []
                colors = []
                # status = []
                # brands = []
                # smoke = []
                for i in range(len(crops)):
                    path = os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', name, 'crops', filenames[i])
                    plate, platetxt = get_plate(path, name)
                    plates.append(plate)
                    # platestxt.append(platetxt)
                    colors.append(get_color(path))
                    # status.append(get_status(path))
                    # brands.append(get_brand(path))
                    # smoke.append(get_smoke(path))
                # # 保存到Image模型中
                #
                # new_image = Image(user=request.user, name=name)
                # new_image.save()

                all_list = zip(labels, crops, plates, colors)
                original_img_path = '/media' + '/vehicle/' + 'images/' + name + '/' + name
                output_img_path = '/media' + '/vehicle/' + 'images/' + name + '/' + 'output.png'
                return render(request, 'try.html',
                              {'form': form, 'img': img, 'all_list': all_list, 'original': original_img_path,
                               'output': output_img_path})
            else:
                form = VehicleForm()


        elif 'video/' in request.FILES['file'].content_type:
            if form.is_valid():
                form.save()
                form = VehicleForm()
                name = request.FILES['file'].name
                # 添加时间戳到文件夹名称
                # timestamp = int(time.time())
                # folder_name = f"{name}_{timestamp}"
                path = os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos', name)
                # # 构建目标路径
                # folder_path = os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos')
                # file_path = os.path.join(folder_path, name)
                # suffix = 1
                # # 检查路径是否存在，如果存在，则加上后缀
                # while True:
                #     file_path1 = os.path.join(folder_path, f"{name}_{suffix}", name)
                #     if not os.path.exists(file_path1):
                #         file_path1 = file_path
                #         break
                #     else:
                #         file_path = file_path1
                #         suffix += 1
                # print(file_path1)
                # try:
                #     os.mkdir(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos', name, "crops"))
                #     os.mkdir(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos', name, "plates"))
                # except OSError:
                #     pass
                get_class_video(path)
                out_video_path = '/media' + '/vehicle/' + 'videos/' + name + '/' + 'output/' + name
                out_video_path = replace_extension(out_video_path)
                smoke, no_smoke = count_video(out_video_path)
                # 保存为.avi格式
                # 调用转码函数，修改为MP4
                avi_to_webm(out_video_path)
                out_video_path = replace_extension2(out_video_path)

                return render(request, 'try.html',
                              {'form': form, 'out_video_path': out_video_path, 'smoke': smoke, 'no_smoke': no_smoke})

        else:
            pass

    return render(request, 'try.html', {'form': form})


def get_class(img_path):
    model = YOLO(r"D:\yolov5\django-yolov8-main\vsmoke\best.pt")  # 加载自定义模型权重
    # model = YOLO(r"D:\yolov5\django-yolov8-main\vclass\best.pt")  # load a custom model
    img_name = os.path.basename(img_path)
    results = model.predict(img_path)
    # 返回检测结果
    img = cv2.imread(img_path)
    crops = []
    # "crops" 用于存放裁剪后的车辆图像
    labels = []
    # "labels" 用于存放标签
    filename_croped = []
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            x1, y1, x2, y2 = result.boxes.xyxy[i].tolist()
            # 检测结果中获取检测到目标的边界框的坐标信息
            x, y, w, h = result.boxes.xywh[i].tolist()
            # 获取检测到目标的边界框的中心坐标以及宽度和高度
            cls = result.boxes.cls[i]
            # 获取检测到目标的类别索引
            conf = result.boxes.conf[i]
            # 获取检测到目标的置信度。
            label = f"{model.names[int(cls)]} {conf:.2f}"
            # 生成标签

            # 若小于大小则进行裁剪
            if h < 1000 and w < 1000:
                crop_image = img[int(y1):int(y2), int(x1):int(x2)]
                filename_croped.append(f'{x1}.png')
                # 文件名
                cv2.imwrite(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', img_name, 'crops', f'{x1}.png'),
                            crop_image)

                cls_l = f"{model.names[int(cls)]}"
                labels.append(cls_l)
                # cls_l = get_smoke(crop_image)  # 调用抽烟检测函数
                # labels.append(cls_l if cls_l != "Unknown" else "No smoking")  # 如果抽烟检测结果为Unknown，则标记为"No smoking"
                cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(img, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                retval, buffer = cv2.imencode('.jpg', crop_image)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                crops.append(image_base64)

    cv2.imwrite(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', img_name, 'output.png'), img)
    # 返回识别结果图片
    retval, buffer = cv2.imencode('.jpg', img)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return crops, labels, image_base64, filename_croped


def get_plate(img_path, original_img_name):
    model = YOLO(r"D:\yolov5\django-yolov8-main\vplate\best.pt")  # load a custom model
    results = model.predict(img_path)
    img = cv2.imread(img_path)
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            if i == 0:
                x1, y1, x2, y2 = result.boxes.xyxy[i].tolist()
                crop_image = img[int(y1):int(y2), int(x1):int(x2)]
                cv2.imwrite(
                    os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', original_img_name, 'plates', f'{x1}.png'),
                    crop_image)
                txt_plate_number = get_platenumber(
                    os.path.join(settings.MEDIA_ROOT, 'vehicle', 'images', original_img_name, 'plates', f'{x1}.png'))
                retval, buffer = cv2.imencode('.jpg', crop_image)
                plate_image_base64 = base64.b64encode(buffer).decode('utf-8')
                return plate_image_base64, txt_plate_number
    return None, "Unknown"


def get_platenumber(img_path):
    regions = ['mx', 'us-ca']  # Change to your country
    token = 'Token dbd16f0a9684d8a881583dff031c7d8c92dbd005'
    with open(img_path, 'rb') as fp:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            data=dict(regions=regions),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': token})
        results = response.json()
        if len(results['results']) > 0:
            return results['results'][0]['plate']
    return "Unknown"


def get_color(img_path):
    image = cv2.imread(img_path)
    # Convert the image to the HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    lower_orange = np.array([10, 70, 50])
    upper_orange = np.array([20, 255, 255])

    lower_yellow = np.array([20, 70, 50])
    upper_yellow = np.array([30, 255, 255])

    lower_green = np.array([30, 70, 50])
    upper_green = np.array([60, 255, 255])

    lower_blue = np.array([100, 70, 50])
    upper_blue = np.array([130, 255, 255])

    lower_purple = np.array([130, 70, 50])
    upper_purple = np.array([160, 255, 255])

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])

    lower_gray = np.array([0, 0, 100])
    upper_gray = np.array([180, 30, 200])

    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 30])

    # Create masks for different colors
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    orange_mask = cv2.inRange(hsv_image, lower_orange, upper_orange)

    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    green_mask = cv2.inRange(hsv_image, lower_green, upper_green)

    blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

    purple_mask = cv2.inRange(hsv_image, lower_purple, upper_purple)

    white_mask = cv2.inRange(hsv_image, lower_white, upper_white)

    gray_mask = cv2.inRange(hsv_image, lower_gray, upper_gray)

    black_mask = cv2.inRange(hsv_image, lower_black, upper_black)

    # Count the number of pixels that belong to each color
    num_red_pixels = cv2.countNonZero(red_mask)
    num_orange_pixels = cv2.countNonZero(orange_mask)
    num_yellow_pixels = cv2.countNonZero(yellow_mask)
    num_green_pixels = cv2.countNonZero(green_mask)
    num_blue_pixels = cv2.countNonZero(blue_mask)
    num_purple_pixels = cv2.countNonZero(purple_mask)

    num_white_pixels = cv2.countNonZero(white_mask)
    num_gray_pixels = cv2.countNonZero(gray_mask)
    num_black_pixels = cv2.countNonZero(black_mask)

    # Estimate the percentage of the image that belongs to each color

    total_pixels = image.shape[0] * image.shape[1]
    red_percentage = int((num_red_pixels / total_pixels) * 100)
    orange_percentage = int((num_orange_pixels / total_pixels) * 100)
    yellow_percentage = int((num_yellow_pixels / total_pixels) * 100)
    green_percentage = int((num_green_pixels / total_pixels) * 100)
    blue_percentage = int((num_blue_pixels / total_pixels) * 100)
    purple_percentage = int((num_purple_pixels / total_pixels) * 100)
    white_percentage = int((num_white_pixels / total_pixels) * 100)
    gray_percentage = int((num_gray_pixels / total_pixels) * 100)
    black_percentage = int((num_black_pixels / total_pixels) * 100)

    # Define the color names and percentages
    colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "White", "Gray", "Black"]
    percentages = [red_percentage, orange_percentage, yellow_percentage, green_percentage, blue_percentage,
                   purple_percentage, white_percentage, gray_percentage, black_percentage]
    max_num, max_idx = max((num, idx) for idx, num in enumerate(percentages))
    color = colors[max_idx]
    return color


def get_status(img_path):
    model = YOLO(r"D:\yolov5\django-yolov8-main\vstatus\best.pt")  # load a custom model
    results = model.predict(img_path)
    img = cv2.imread(img_path)
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            if i >= 0:
                return "Damaged"
        return "Not Damaged"


def get_brand(img_path):
    model = YOLO(r"D:\yolov5\django-yolov8-main\vbrand\best.pt")  # load a custom model
    results = model.predict(img_path)
    for result in results:
        for i in range(len(result.boxes.xyxy)):
            if i == 0:
                cls = result.boxes.cls[i]
                cls_l = f"{model.names[int(cls)]}"
                return cls_l
    return "Unknown"


" Video "


def get_class_video(video_path):
    model = YOLO(r"D:\yolov5\django-yolov8-main\vsmoke\best.pt")
    video_name = os.path.basename(video_path)
    # print(video_name)
    model.predict(video_path, save=True, project=settings.BASE_DIR,
                  name=os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos', video_name, 'output'))
    # # 在预测结束后调用转码函数
    # out_video_path = '/media' + '/vehicle/' + 'videos/' + video_name + '/' + 'output/' + video_name
    # avi_to_mp4(out_video_path)


def avi_to_mp4(out_avi_path):
    avi_path = "D:/yolov5/django-yolov8-main" + out_avi_path
    output_mp4_path = replace_extension1(avi_path)
    print(output_mp4_path)
    print(avi_path)
    # 打开AVI文件
    cap = cv2.VideoCapture(avi_path)
    print(cap)
    # if not cap.isOpened():
    #     print("Error: Unable to open AVI file.")
    #     return

    # 获取AVI文件的基本信息
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 定义输出MP4文件的编解码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用H.264编解码器

    # 创建 VideoWriter 对象来保存为MP4文件
    out = cv2.VideoWriter(output_mp4_path, fourcc, fps, (width, height))
    if not out.isOpened():
        print("Error: Unable to create MP4 file.")
        cap.release()
        return

    # 读取AVI文件中的每一帧并写入MP4文件
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    # 释放资源
    cap.release()
    out.release()
    print("AVI to MP4 conversion completed successfully.")


def avi_to_webm(out_avi_path):
    avi_path = "D:/yolov5/django-yolov8-main" + out_avi_path
    output_webm_path = replace_extension2(avi_path)  # 定义替换扩展名的函数
    # print(output_webm_path)
    # print(avi_path)

    # 打开AVI文件
    cap = cv2.VideoCapture(avi_path)
    # print(cap)

    # 获取AVI文件的基本信息
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 定义输出WebM文件的编解码器
    fourcc = cv2.VideoWriter_fourcc(*'vp80')  # 使用VP8编解码器

    # 创建 VideoWriter 对象来保存为WebM文件
    out = cv2.VideoWriter(output_webm_path, fourcc, fps, (width, height))
    if not out.isOpened():
        print("Error: Unable to create WebM file.")
        cap.release()
        return

    # 读取AVI文件中的每一帧并写入WebM文件
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)

    # 释放资源
    cap.release()
    out.release()
    print("AVI to WebM conversion completed successfully.")


def replace_extension(filepath, new_extension='avi'):
    """
    Replace the extension of a file path with a specified extension.

    Args:
        filepath (str): The file path to modify.
        new_extension (str): The new extension to use.

    Returns:
        str: The modified file path.
    """
    # Split the file path into its base name and extension
    base_path, old_extension = os.path.splitext(filepath)

    # Create the new file path with the desired extension
    new_filepath = base_path + '.' + new_extension

    return new_filepath


def replace_extension1(filepath, new_extension='mp4'):
    """
    Replace the extension of a file path with a specified extension.

    Args:
        filepath (str): The file path to modify.
        new_extension (str): The new extension to use.

    Returns:
        str: The modified file path.
    """
    # Split the file path into its base name and extension
    base_path, old_extension = os.path.splitext(filepath)

    # Create the new file path with the desired extension
    new_filepath = base_path + '.' + new_extension

    return new_filepath


def replace_extension2(filepath, new_extension='webm'):
    """
    Replace the extension of a file path with a specified extension.

    Args:
        filepath (str): The file path to modify.
        new_extension (str): The new extension to use.

    Returns:
        str: The modified file path.
    """
    # Split the file path into its base name and extension
    base_path, old_extension = os.path.splitext(filepath)

    # Create the new file path with the desired extension
    new_filepath = base_path + '.' + new_extension

    return new_filepath


# 显示视频统计结果
def count_video(video_path):
    # 打开视频文件
    model = YOLO(r"D:\yolov5\django-yolov8-main\vsmoke\best.pt")
    video_path = "D:/yolov5/django-yolov8-main" + video_path
    cap = cv2.VideoCapture(video_path)

    frame_count = 0  # 初始化帧计数器

    counts = defaultdict(int)

    while cap.isOpened():  # 检查视频文件是否成功打开
        ret, frame = cap.read()  # 读取视频文件中的下一帧,ret 是一个布尔值，如果读取帧成功
        if not ret:
            break

        results = model(frame)

        for result in results:
            for box in result.boxes:
                class_id = result.names[box.cls[0].item()]
                counts[class_id] += 1

        frame_count += 1  # 更新帧计数器

    # 组织输出结果
    smoke_count = counts.get("smoke", 0)
    no_smoke_count = sum(counts.values()) - smoke_count
    print(smoke_count, no_smoke_count)

    return smoke_count, no_smoke_count

# # 导出为webm格式
#
# def replace_extension(file_path, new_extension):
#     """
#     Replace the file extension in the given file path with the new extension.
#     """
#     base_name = os.path.basename(file_path)
#     file_name, _ = os.path.splitext(base_name)
#     return os.path.join(os.path.dirname(file_path), file_name + new_extension)
#
# def get_class_video_webm(video_path):
#     """
#     Process the input video with some functionality and save the output video in WebM format.
#     """
#     # Define the output video path with WebM extension
#     output_video_path = replace_extension(video_path, '.webm')
#
#     # Define the codec and create VideoWriter object
#     fourcc = cv2.VideoWriter_fourcc(*'VP80')
#     cap = cv2.VideoCapture(video_path)
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
#
#     # Process each frame of the input video and write to the output video
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         # Add your processing logic here
#         # For example, you can apply object detection using YOLO or any other method
#         # and then modify the frame accordingly
#         # frame = process_frame(frame)
#         out.write(frame)
#
#     # Release resources
#     cap.release()
#     out.release()
#
#     return output_video_path
#
#     if form.is_valid():
#         form.save()
#         form = VehicleForm()
#         name = request.FILES['file'].name
#         path = os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos', name)
#         try:
#             os.mkdir(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos', name, "crops"))
#             os.mkdir(os.path.join(settings.MEDIA_ROOT, 'vehicle', 'videos', name, "plates"))
#         except OSError:
#             pass
#         # Process the input video and save the output video in WebM format
#         out_video_path = get_class_video_webm(path)
#         return render(request, 'try.html', {'form': form, 'out_video_path': out_video_path})
