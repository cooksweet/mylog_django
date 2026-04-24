# blog/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Article, Category
import requests
from django.utils import timezone
import calendar
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CommentForm
from .models import Comment
from myblog import settings
from django.core.cache import cache

def index(request):
    """主页视图：展示最新文章卡片、分类导航、日历（静态占位）"""
    """主页视图：动态日期、天气、最新文章"""
    # ---------- 获取当前日期时间 ----------
    now = timezone.now()  # Django时区感知的当前时间
    current_date = now

    # ---------- 获取天气信息（和风天气预报） ----------
    weather_desc = "晴"  # 默认值
    temperature = 22  # 默认温度
    icon_code = "100"  # 默认图标代码
    weather = get_weather_data()
    if weather:
        weather_desc = weather['text']
        temperature = weather['temp']
        icon_code = weather['icon']  # 和风天气图标数字，如 100、101 等

        # 和风天气图标映射（免费版可使用他们的 SVG 图标，引入 CDN）
        # 直接使用图标字体或图片，这里使用和风天气提供的图标 CDN（https://icons.qweather.com/）
    weather_icon_url = f"../../static/QWeather-Icons-1.8.0/icons/{icon_code}.svg"

    # ---------- 生成动态日历 ----------
    year = now.year
    month = now.month
    today = now.day

    # 获取该月的日历矩阵（周列表，每周为一个列表，包含7天的日期，0表示不属于本月）
    cal = calendar.Calendar(firstweekday=6)  # 周日作为一周的第一天
    month_days = cal.monthdayscalendar(year, month)

    # 月份名称和年份
    month_name = now.strftime('%Y年%m月')

    # 获取最近发布的4篇文章用于右侧卡片展示
    recent_articles = Article.objects.all()[:4]
    # 获取各分类最新一篇文章（可选，用于“更多推荐”）
    latest_life = Article.objects.filter(category=Category.LIFE).first()
    latest_learning = Article.objects.filter(category=Category.LEARNING).first()
    latest_travel = Article.objects.filter(category=Category.TRAVEL).first()
    latest_reflection = Article.objects.filter(category=Category.REFLECTION).first()

    context = {
        # 天气数据
        'current_date': current_date,
        'weather_desc': weather_desc,
        'temperature': temperature,
        'weather_icon_url': weather_icon_url,

        'recent_articles': recent_articles,
        'latest_life': latest_life,
        'latest_learning': latest_learning,
        'latest_travel': latest_travel,
        'latest_reflection': latest_reflection,
        # 日历数据
        'calendar_year': year,
        'calendar_month': month,
        'calendar_month_name': month_name,
        'calendar_weeks': month_days,
        'today': today,

    }
    return render(request, 'blog/index.html', context)

def category_articles(request, category_slug):
    """分类文章列表页"""
    # 将URL中的英文分类转换为模型使用的值
    category_map = {
        'life': Category.LIFE,
        'learning': Category.LEARNING,
        'travel': Category.TRAVEL,
        'reflection': Category.REFLECTION,
    }
    category_value = category_map.get(category_slug)
    if not category_value:
        # 无效分类返回404
        from django.http import Http404
        raise Http404("分类不存在")

    articles_list = Article.objects.filter(category=category_value)
    category_name = dict(Category.choices).get(category_value)

    # 分页：每页4篇文章
    paginator = Paginator(articles_list, 4)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    context = {
        'category_name': category_name,
        'category_slug': category_slug,
        'articles': articles,
    }
    return render(request, 'blog/category.html', context)

def article_detail(request, article_id):
    """文章详情页"""
    article = get_object_or_404(Article, pk=article_id)
    comments = article.comments.filter(active=True)  # 只显示启用的评论
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.save()
            # 重定向到当前页，避免重复提交（使用锚点定位到评论列表）
            from django.shortcuts import redirect
            return redirect(f'/article/{article.id}/#comments-section')
    context = {
        'article': article,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)

def search_articles(request):
    """文章搜索"""
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        # 在标题和内容中搜索
        results = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).distinct()
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'blog/search.html', context)

def get_weather_data():
    """获取天气信息，优先读取缓存，缓存失效后重新请求"""

    cache_key = 'homepage_weather'

    # 1. 优先读取缓存
    weather_data = cache.get(cache_key)
    if weather_data is not None:
        print("使用的是缓存天气")
        return weather_data

    # 2. 缓存不存在，调用和风天气API
    print("使用的是请求天气")
    url = 'https://nu7byhjwbb.re.qweatherapi.com/v7/weather/now'
    params = {
        'location': settings.WEATHER_LOCATION_ID,
        'key': settings.WEATHER_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data.get('code') == '200':
            now = data['now']

            weather_data = {
                'temp': now.get('temp'),
                'text': now.get('text'),
                'icon': now.get('icon'),
                'wind_dir': now.get('windDir'),
                'wind_scale': now.get('windScale'),
                'humidity': now.get('humidity'),
                'obs_time': now.get('obsTime'),
                'city': settings.WEATHER_CITY_NAME,
            }

            # 3. 写入缓存（1小时）
            cache.set(cache_key, weather_data, 3600)
            return weather_data

    except Exception as e:
        print(f'天气接口请求失败: {e}')

    return None