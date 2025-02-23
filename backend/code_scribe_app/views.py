import mistune
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Article  # import Article model
from django.views.decorators.csrf import csrf_exempt
from code_scribe_app.test_model import generate_markdown


# def model_processing(command):
#     """模拟模型返回 Markdown"""
#     if command == "generate summary":
#         # 需要和model链接
#         md_result = generate_markdown("Summarize the importance of AI in 3 sentences.")
#         return md_result
#     else:
#         return "# Error\nInvalid command."

# command needs to be string
def model_processing(command):
    """use the model to generate markdown"""
    md_result = generate_markdown(command)  # Pass the real command
    return md_result if md_result else "# Error\nInvalid command."


# parse_markdown function

def parse_markdown(content):
    """Convert Markdown to JSON-like AST format"""
    if not content.strip():  # Ensure content is not empty
        return [{"type": "error", "message": "Empty Markdown content"}]

    parser = mistune.create_markdown(renderer="ast")
    ast = parser(content)
    print("DEBUG: Parsed AST Structure:", ast)  # Debug log
    return ast




def paginate_markdown(article_id, page_number, page_size=1):
    """Paginate the Markdown content of an article"""
    article = get_object_or_404(Article, id=article_id)
    ast = parse_markdown(article.content)

    pages = []
    current_page = []
    
    for block in ast:
        if block["type"] == "heading":
            level = block.get("attrs", {}).get("level")  # get heading level
            if level == 1:
                if current_page:
                    pages.append(current_page)
                current_page = [block]
        else:
            current_page.append(block)

    if current_page:
        pages.append(current_page)

    total_pages = len(pages)

    if page_number < 1 or page_number > total_pages:
        return JsonResponse({
            "status": "error",
            "message": "Page number out of range",
            "total_pages": total_pages
        }, status=400)

    return JsonResponse({
        "status": "success",
        "message": "Retrieved page successfully",
        "data": {
            "page": page_number,
            "page_size": page_size,
            "total_pages": total_pages,
            "content": pages[page_number - 1]
        }
    })


# we don't need this anymore
# # API 路由
# def markdown_view(request, article_id):
#     """處理 API 請求，返回指定文章 & 頁碼的 Markdown JSON"""
#     page_number = int(request.GET.get('page', 1))  # 頁碼從 GET 參數獲取
#     return paginate_markdown(article_id, page_number)


# api route
@csrf_exempt
def process_model_request(request):
    """处理前端请求，把指令交给模型处理，并返回 JSON"""
    print(f"Received request: {request.body}")  # Debugging log
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data
            command = data.get("command", "").strip()

            if not command:
                return JsonResponse({"status": "error", "message": "Input cannot be empty"}, status=400)

            # get the markdown string
            markdown_str = model_processing(command)

            # turn the markdown string into AST
            ast = parse_markdown(markdown_str)

            return JsonResponse({
                "status": "success",
                "message": "Generated markdown successfully",
                "data": {"doc": ast}
            })

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


# home page
def home(request):
    return HttpResponse("Welcome to CodeScribe!")
