# code_scribe_app/urls.py
# from django.urls import path
# from . import views



# code_scribe_app/urls.py
from django.urls import path
from .views import home, process_model_request  # 只保留用到的视图

urlpatterns = [
    path('', home, name='home'),  # 主页
    path('process/', process_model_request, name='process_model_request'),  # 处理模型请求
]
