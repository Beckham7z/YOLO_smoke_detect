from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
import os
from urllib.parse import urlparse
# Create your models here.
def dynamic_path(instance, filename):
    extension = instance.file.name.split('.')[-1]
    if extension in ['jpg', 'jpeg', 'png', 'gif']:
        return f"vehicle/images/{instance.file}/{filename}"
    elif extension in ['mp4', 'mov', 'avi', 'wmv','webm']:
        return f"vehicle/videos/{instance.file}/{filename}"
    # extension = instance.file.name.split('.')[-1]
    # # 定义目标文件夹路径
    # folder_path = ""
    # if extension in ['jpg', 'jpeg', 'png', 'gif']:
    #     folder_path = "vehicle/images"
    # elif extension in ['mp4', 'mov', 'avi', 'wmv', 'webm']:
    #     folder_path = "vehicle/videos"
    # else:
    #     return None
    #
    # # 获取文件名（不包含扩展名）
    # file_name = os.path.splitext(filename)[0]
    #
    # # 初始后缀序号为0
    # suffix = 0
    #
    # # 构建初始路径
    # target_path = os.path.join(folder_path, instance.file.name,  file_name)
    #
    # # 检查路径是否存在，如果存在，则加上后缀
    # while os.path.exists(target_path):
    #     suffix += 1
    #     # 重新构建路径
    #     target_path = os.path.join(folder_path,  f"{instance.file.name}_{suffix}",  file_name)
    #
    # return target_path

def dynamic_path2(instance, filename):
    # 获取文件的扩展名
    extension = filename.split('.')[-1]
    # 根据扩展名确定存储路径
    if extension in ['jpg', 'jpeg', 'png', 'gif']:
        return f"vehicle/images/examine/{instance.images}/{filename}"
    elif extension in ['mp4', 'mov', 'avi', 'wmv', 'webm']:
        return f"vehicle/videos/{filename}"

def dynamic_path3(instance, filename):
    print(instance.images)
    extension = filename.split('.')[-1]
    # 根据扩展名确定存储路径
    if extension in ['jpg', 'jpeg', 'png', 'gif']:
        return f"vehicle/images/examine/{instance.photo}/{filename}"
    elif extension in ['mp4', 'mov', 'avi', 'wmv', 'webm']:
        return f"vehicle/videos/{filename}"

def validate_file_extension(value):
    valid_extensions = ['.png', '.jpg', '.jpeg','.mp4','.mov','.avi','.wmv','.webm']
    file_extension = os.path.splitext(value.name)[1]
    if file_extension not in valid_extensions:
        raise ValidationError('Only png , jpg , jpeg, mp4 , mov , avi , wmv and webm files are allowed.')  
      
'''def validate_image_size(value):
    if value.size > 10485760:  # 10 MB
        raise ValidationError('File size cannot exceed 10 MB.')    
 '''   
class Vehicle(models.Model):
    file = models.FileField(verbose_name='',upload_to=dynamic_path , blank=False , null=False ,validators=[validate_file_extension])
    def __str__(self):
        return f"{self.id}"

class Smoke(models.Model):
    images = models.FileField(verbose_name='',upload_to=dynamic_path2 , blank=False , null=False ,validators=[validate_file_extension])
    def __str__(self):
        return f"{self.id}"

from django.contrib.auth.models import User

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 添加一个外键字段来关联用户
    name = models.CharField(max_length=100)
    image_file = models.ImageField(upload_to='images/')
    output_image_file = models.ImageField(upload_to='images/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# class CustomUser(AbstractUser):
#     # Add custom fields here
#
#     class Meta:
#         verbose_name = 'Custom User'
#         verbose_name_plural = 'Custom Users'
#
# # Add related_name to avoid clashes with built-in User model
# CustomUser.groups.field.related_name = 'customuser_groups'
# CustomUser.user_permissions.field.related_name = 'customuser_user_permissions'

# class CrawledImage(models.Model):
#     url = models.URLField(verbose_name='Image URL', unique=True)
#     photo = models.ImageField(verbose_name='Image', upload_to=dynamic_path3, blank=False , null=False ,validators=[validate_file_extension])
#
#     def __str__(self):
#         return self.url
'''
class Vehicle(models.Model):
    CLASS_CHOICES = [
        ("car", "Car"),
        ("motorbike", "Motorbike"),
        ("truck", "Truck"),
        ("van", "Van"),
        ("bus", "Bus"),
    ]
    COLOR_CHOICES = [
        ("red", "Red"),
        ("green", "Green"),
        ("blue", "Blue"),
        ("yellow", "Yellow"),
        ("orange", "Orange"),
        ("white", "White"),
        ("gray", "Grey"),
        ("black", "Black"),
        ("purple", "Purple"),
    ]
    BRAND_CHOICES = [
        # Audi, Chevrolet, Dodge, GMC, Honda, Hyundai, Jeep, Mazda, Mercedes, Mitsubishi, Nissan, Toyota, Volkswagen, bmw, dodge, ford, kia, suzuki, volvo
        ("Audi", "Audi"),
        ("Chevrolet", "Chevrolet"),
        ("Dodge", "Dodge"),
        ("GMC", "GMC"),
        ("Honda", "Honda"),
        ("Hyundai", "Hyundai"),
        ("Jeep", "Jeep"),
        ("Mazda", "Mazda"),
        ("Mercedes", "Mercedes Benz"),
        ("Mitsubishi", "Mitsubishi"),
        ("Nissan", "Nissan"),
        ("Toyota", "Toyota"),
        ("Volkswagen", "Volkswagen"),
        ("bmw", "BMW"),
        ("Ford", "Ford"),
        ("kia", "KIA"),
        ("suzuki", "Suzuki"),
        ("volvo", "Volvo"),
    ]
    STATUS_CHOICES = [
        ('damaged',"Damaged"),
        ('not-damaged',"Not Damaged")
    ]
    name = models.CharField(
        verbose_name="Class", choices=CLASS_CHOICES, max_length=20, blank=True
    )
    brand = models.CharField(verbose_name="Brand", choices=BRAND_CHOICES ,max_length=20, blank=True)
    color = models.CharField(
        verbose_name="Color", choices=COLOR_CHOICES, max_length=20, blank=True
    )
    status = models.CharField(verbose_name="Status", choices=STATUS_CHOICES ,max_length=20, blank=True)
    speed = models.FloatField(verbose_name="Speed", blank=True , null=True)
    file = models.FileField(
        verbose_name="Image Or Video", upload_to='vehicle/'
    )
    platenumber = models.ImageField(
        verbose_name="Plate Number",
        upload_to='plate/',
        blank=True,
    )

    def __str__(self):
        return f"{self.id}"
'''


"""
Choice field
list of tuples[(x,y),(),....], where the first element of each tuple is the value to be submitted and the second element is the human-readable label to be displayed to the user.
"""
