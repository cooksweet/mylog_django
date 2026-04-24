# blog/admin.py

from django.contrib import admin
from .models import Article
from django_summernote.admin import SummernoteModelAdmin
from .models import Comment

@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    list_display = ('title', 'category', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    summernote_fields = ('content',)          # 指定富文本字段
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'summary', 'category', 'image')
        }),
    )

    @admin.register(Comment)
    class CommentAdmin(admin.ModelAdmin):
        list_display = ('author', 'article', 'created', 'active')
        list_filter = ('active', 'created')
        search_fields = ('author', 'body')
        actions = ['make_inactive']

        def make_inactive(self, request, queryset):
            queryset.update(active=False)

        make_inactive.short_description = "标记为不可见"