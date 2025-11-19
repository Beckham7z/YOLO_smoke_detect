from django.urls import path
from . import views

urlpatterns = [
    path('', view = views.login_in, name='login'),  # 将默认路径指向登录页面
    path('index/',view=views.index , name="index"),
    path('try/',view=views.try_ , name="try"),
    path('exmaine/',view=views.examine_batch_photo , name="examine"),
    path('111/',view=views.examine_url , name="111"),
    path('register/', view=views.register, name='register'),
    path('user/', view=views.user, name='user'),
]