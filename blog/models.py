# blog/models.py

from django.db import models
from django.utils import timezone

class Category(models.TextChoices):
    """文章分类选项"""
    LIFE = 'life', '生活'
    LEARNING = 'learning', '学习'
    TRAVEL = 'travel', '旅游'
    REFLECTION = 'reflection', '感悟'

class Article(models.Model):
    """博客文章模型"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    summary = models.CharField(max_length=300, blank=True, verbose_name='摘要')
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.LIFE,
        verbose_name='分类'
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    # 可选图片字段，若未上传则使用默认占位图
    image = models.ImageField(upload_to='articles/%Y/%m/', blank=True, null=True, verbose_name='文章图片')

    class Meta:
        ordering = ['-created_at']          # 按创建时间倒序
        verbose_name = '文章'
        verbose_name_plural = '文章管理'

    def __str__(self):
        return self.title

    def get_category_display_cn(self):
        """返回分类中文名"""
        return dict(Category.choices).get(self.category, self.category)

class Comment(models.Model):
    """文章评论模型（无需登录）"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='所属文章')
    author = models.CharField(max_length=50, verbose_name='昵称')
    body = models.TextField(verbose_name='评论内容')
    created = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    active = models.BooleanField(default=True, verbose_name='是否显示')  # 可后台管理屏蔽

    class Meta:
        ordering = ['created']
        verbose_name = '评论'
        verbose_name_plural = '评论管理'

    def __str__(self):
        return f'{self.author} 对 {self.article} 的评论'