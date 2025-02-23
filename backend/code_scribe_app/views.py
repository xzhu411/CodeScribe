# import mistune
# import json
# import os
# from django.http import JsonResponse, HttpResponse
# from rest_framework import viewsets
# from django.shortcuts import get_object_or_404
# from .models import Article
# from .serializer import ArticleSerializer
# import sys
# import os
# from django.views.decorators.csrf import csrf_exempt

# # class ArticleViewSet(viewsets.ViewSet):
# #     def list(self, request):
# #         queryset = Article.objects.all()
# #         serializer = ArticleSerializer(queryset, many=True)
# #         return JsonResponse(serializer.data, safe=False)

# #     def create(self, request):
# #         serializer = ArticleSerializer(data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return JsonResponse(serializer.data, status=201)
# #         return JsonResponse(serializer.errors, status=400)

# #     def retrieve(self, request, pk=None):
# #         queryset = Article.objects.all()
# #         article = get_object_or_404(queryset, pk=pk)
# #         serializer = ArticleSerializer(article)
# #         return JsonResponse(serializer.data)

# #     def update(self, request, pk=None):
# #         article = Article.objects.get(pk=pk)
# #         serializer = ArticleSerializer(article, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return JsonResponse(serializer.data)
# #         return JsonResponse(serializer.errors, status=400)

# #     def destroy(self, request, pk=None):
# #         article = Article.objects.get(pk=pk)
# #         article.delete()
# #         return HttpResponse(status=204)


# # 计算 llm_core 目录的绝对路径
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取 backend 目录
# parent_path=os.path.dirname(BASE_DIR)
# LLM_CORE_PATH = parent_path+'/'  # 计算 llm_core 的路径
# print(f"parent_path: {parent_path}")  # Debug log
# print(f"LLM_CORE_PATH: {LLM_CORE_PATH}")  # Debug log

# sys.path.append(LLM_CORE_PATH)  # ✅ 添加到 Python 路径

# # 现在可以导入 llm_core 里的模块

# from llm_core.api import CoreLLM  # Ensure correct import of CoreLLM
# from llm_core.utils import traverse_directory

# # Get the current directory path
# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # Initialize the LLM model
# llm = CoreLLM(verbose=False)
# llm.load_model("Gemini 2.0 Flash")  # You can replace this with your own LLM

# def parse_markdown(content=None, file_path=None):
#     """
#     Parse Frontend directory input Markdown content or file into an AST JSON structure.
#     """
#     if file_path:
#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()
    
#     if content is None:
#         raise ValueError("Markdown content or file path must be provided")

#     parser = mistune.create_markdown(renderer=mistune.AstRenderer())
#     return parser(content)


# def extract_text(block):
#     """
#     Extract textual content from a Markdown AST block.
#     """
#     if block["type"] in ["paragraph", "block_code", "list", "blockquote"]:
#         if "children" in block:
#             return "".join(child["text"] for child in block["children"] if "text" in child)
#         return block.get("text", "")
#     return ""

# def replace_code_with_model_output(name, nested_dict, return_type="md"):
#     """
#     Traverse the nested structure and replace Python code with model-generated content.
#     """
#     for key, value in nested_dict.items():
#         if isinstance(value, dict):
#             replace_code_with_model_output(name, value)
#         elif isinstance(value, str):
#             print("Sending code to LLM for generation...")  # Debug log
#             generated_md = llm(value)  # Let CoreLLM generate new Markdown
#             if return_type == "md":
#                 nested_dict[key] = generated_md
#             else:
#                 nested_dict[key] = extract_text(generated_md)
#     # Save generated content to a new file
#     with open(f"gen_doc/{name}.md", "w", encoding="utf-8") as f:
#         f.write(json.dumps(nested_dict, ensure_ascii=False, indent=2))

# @csrf_exempt
# def markdown_view(request):
#     """
#     Django API view to return a structured Markdown AST JSON.
#     """
#     if request.method == "POST":
#         try:
#             # Ensure request body is JSON
#             import json
#             data = json.loads(request.body)

#             root_dir = data.get("root_dir")  # Extract root_dir from request body
#             if not root_dir:
#                 return JsonResponse({"error": "root_dir is required"}, status=400)

#             # Process the data
#             structured_data = traverse_directory(root_dir)  # Assuming function exists
#             codebase_name = os.path.basename(os.path.normpath(root_dir))
#             replace_code_with_model_output(codebase_name, structured_data)

#             return JsonResponse(structured_data, json_dumps_params={"ensure_ascii": False, "indent": 2})

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON format"}, status=400)

#     return JsonResponse({"error": "Invalid request method"}, status=405)



# def home(request):
#     """
#     Homepage view with a simple welcome message.
#     """
#     return HttpResponse("Welcome to CodeScribe!")

import mistune
import json
import os
import sys
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from llm_core.api import CoreLLM  # Ensure correct import of CoreLLM
from llm_core.utils import traverse_directory

# Initialize CoreLLM
llm = CoreLLM(verbose=False)
llm.load_model("Gemini 2.0 Flash")  # You can replace this with your own LLM

# Helper functions for markdown parsing and code generation
def parse_markdown(content=None, file_path=None):
    """
    Parse Frontend directory input Markdown content or file into an AST JSON structure.
    """
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    if content is None:
        raise ValueError("Markdown content or file path must be provided")

    parser = mistune.create_markdown(renderer=mistune.AstRenderer())
    return parser(content)

def extract_text(block):
    """
    Extract textual content from a Markdown AST block.
    """
    if block["type"] in ["paragraph", "block_code", "list", "blockquote"]:
        if "children" in block:
            return "".join(child["text"] for child in block["children"] if "text" in child)
        return block.get("text", "")
    return ""

def replace_code_with_model_output(name, nested_dict, return_type="md"):
    """
    Traverse the nested structure and replace Python code with model-generated content.
    """
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            replace_code_with_model_output(name, value)
        elif isinstance(value, str):
            print("Sending code to LLM for generation...")  # Debug log
            generated_md = llm(value)  # Let CoreLLM generate new Markdown
            if return_type == "md":
                nested_dict[key] = generated_md
            else:
                nested_dict[key] = extract_text(generated_md)
    
    # Save generated content to a new file
    with open(f"gen_doc/{name}.md", "w", encoding="utf-8") as f:
        f.write(json.dumps(nested_dict, ensure_ascii=False, indent=2))

@csrf_exempt
def markdown_view(request):
    """
    Django API view to return a structured Markdown AST JSON.
    """
    if request.method == "POST":
        try:
            # Ensure request body is JSON
            data = json.loads(request.body)

            # root_dir = data.get("root_dir")  # Extract root_dir from request body
            root_dir = data.get("directory_path", "").strip()
            if not root_dir:
                return JsonResponse({"error": "root_dir is required"}, status=400)

            # Process the data
            structured_data = traverse_directory(root_dir)  # Assuming function exists
            codebase_name = os.path.basename(os.path.normpath(root_dir))
            replace_code_with_model_output(codebase_name, structured_data)

            return JsonResponse(structured_data, json_dumps_params={"ensure_ascii": False, "indent": 2})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# Home Page
def home(request):
    """
    Homepage view with a simple welcome message.
    """
    return HttpResponse("Welcome to CodeScribe!")
