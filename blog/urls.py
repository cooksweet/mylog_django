# blog/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),                           # 主页
    path('category/<slug:category_slug>/', views.category_articles, name='category'),  # 分类列表
    path('article/<int:article_id>/', views.article_detail, name='article_detail'),    # 文章详情
    path('search/', views.search_articles, name='search'),         # 搜索页
]