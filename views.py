import mistune
import json
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Article
from llm_core.api import CoreLLM  # 確保正確導入 CoreLLM

# Get the current directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 初始化 LLM 模型
llm = CoreLLM(verbose=False)
llm.load_model("Gemini 2.0 Flash")  # 你可以換成自己的 LLM

def parse_markdown(content=None, file_path=None):
    """
    Parse Markdown content or file into an AST JSON structure.
    """
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    if content is None:
        raise ValueError("Markdown content or file path must be provided")

    parser = mistune.create_markdown(renderer=mistune.AstRenderer())
    return parser(content)

def build_nested_structure(ast):
    """
    Convert the Markdown AST into a nested JSON structure.
    """
    root = {}
    stack = [(root, 0)]  # (current level dictionary, heading level)

    for block in ast:
        if block["type"] == "heading":
            level = block["level"]
            title = block["children"][0]["text"]

            new_section = {}
            while stack and stack[-1][1] >= level:
                stack.pop()
            
            stack[-1][0][title] = new_section
            stack.append((new_section, level))

        else:
            text_content = extract_text(block)
            if text_content:
                stack[-1][0]["content"] = stack[-1][0].get("content", "") + "\n" + text_content

    return root

def extract_text(block):
    """
    Extract textual content from a Markdown AST block.
    """
    if block["type"] in ["paragraph", "block_code", "list", "blockquote"]:
        if "children" in block:
            return "".join(child["text"] for child in block["children"] if "text" in child)
        return block.get("text", "")
    return ""

def replace_code_with_model_output(nested_dict):
    """
    Traverse nested structure and replace Python code with model-generated content.
    """
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            replace_code_with_model_output(value)
        elif key == "content" and "```python" in value:
            print("Sending code to LLM for generation...")  # Debug log
            generated_md = llm(value)  # 讓 CoreLLM 生成新的 Markdown
            nested_dict[key] = generated_md

def markdown_view(request, article_id):
    """
    Django API view to return a structured Markdown AST JSON.
    """
    if article_id == 0:
        ast = parse_markdown(file_path=os.path.join(BASE_DIR, "test.md"))
    else:
        article = get_object_or_404(Article, id=article_id)
        ast = parse_markdown(article.content)

    structured_data = build_nested_structure(ast)
    replace_code_with_model_output(structured_data)
    
    return JsonResponse(structured_data, json_dumps_params={"ensure_ascii": False, "indent": 2})

def home(request):
    """
    Homepage view with a simple welcome message.
    """
    return HttpResponse("Welcome to CodeScribe!")
