import mistune
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Article  # 確保你的 models.py 有 Article 模型

# 解析 Markdown 為 JSON
def parse_markdown(content):
    """將 Markdown 轉換為 JSON（AST 格式）"""
    parser = mistune.create_markdown(renderer=mistune.AstRenderer())  # 修正 renderer
    return parser(content)

# 分頁邏輯
def paginate_markdown(article_id, page_number, page_size=1):
    """根據文章 ID 提取 Markdown，轉換為 JSON，並進行分頁"""
    article = get_object_or_404(Article, id=article_id)
    ast = parse_markdown(article.content)

    # 根據 H1 標題劃分頁面
    pages = []
    current_page = []
    for block in ast:
        if block["type"] == "heading" and block["level"] == 1:
            if current_page:
                pages.append(current_page)
            current_page = [block]
        else:
            current_page.append(block)

    if current_page:
        pages.append(current_page)

    total_pages = len(pages)

    if page_number < 1 or page_number > total_pages:
        return JsonResponse({"error": "頁碼超出範圍", "total_pages": total_pages}, status=400)

    return JsonResponse({
        "page": page_number,
        "page_size": page_size,
        "total_pages": total_pages,
        "content": pages[page_number - 1]
    })

# API 路由
def markdown_view(request, article_id):
    """處理 API 請求，返回指定文章 & 頁碼的 Markdown JSON"""
    page_number = int(request.GET.get('page', 1))  # 頁碼從 GET 參數獲取
    return paginate_markdown(article_id, page_number)

# 主页视图
def home(request):
    return HttpResponse("欢迎来到 CodeScribe！")
