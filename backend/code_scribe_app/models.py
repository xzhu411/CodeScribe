from django.db import models

# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=200)  # 文章標題
    content = models.TextField()  # Markdown 內容
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
