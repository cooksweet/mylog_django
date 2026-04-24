from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'body']
        labels = {
            'author': '昵称',
            'body': '评论内容',
        }
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入昵称'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '写下你的想法...'}),
        }