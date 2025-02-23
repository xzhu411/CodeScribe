# # code_scribe_app/urls.py
# from django.urls import path
# from .views import markdown_view, home

# urlpatterns = [
#     path('', home, name="home"),
#     path('message/', markdown_view, name='message'),
# ]

# code_scribe_app/urls.py
from django.urls import path
# from .views import home, process_model_request  # 只保留用到的视图
from .views import home, markdown_view

urlpatterns = [
    path('', home, name='home'),  # 主页
    # path('process/', process_model_request, name='process_model_request'),  # 处理模型请求
    path('process/', markdown_view, name='markdown_view'),  # 处理模型请求
]
