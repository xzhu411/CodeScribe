import mistune
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Article  # Ensure your models.py has an Article model
import os

# Get the current directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_markdown(content=None, file_path=None):
    """
    Parse Markdown content or file into an AST JSON structure.
    :param content: Markdown content as a string
    :param file_path: Path to a Markdown file
    :return: Parsed AST JSON
    """
    if file_path:  # If a file path is provided, read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    
    if content is None:
        raise ValueError("Markdown content or file path must be provided")

    parser = mistune.create_markdown(renderer=mistune.AstRenderer())
    return parser(content)

def build_nested_structure(ast):
    """
    Convert the Markdown AST into a nested JSON structure.
    :param ast: Parsed Markdown AST JSON
    :return: Nested dictionary
    """
    root = {}
    stack = [(root, 0)]  # (current level dictionary, heading level)

    for block in ast:
        if block["type"] == "heading":
            level = block["level"]
            title = block["children"][0]["text"]

            # Create a new section
            new_section = {}
            while stack and stack[-1][1] >= level:
                stack.pop()
            
            stack[-1][0][title] = new_section
            stack.append((new_section, level))

        else:
            # Convert other Markdown elements to plain text
            text_content = extract_text(block)
            if text_content:
                stack[-1][0]["content"] = stack[-1][0].get("content", "") + "\n" + text_content

    return root

def extract_text(block):
    """
    Extract textual content from a Markdown AST block.
    :param block: A single AST block
    :return: Plain text content
    """
    if block["type"] in ["paragraph", "block_code", "list", "blockquote"]:
        if "children" in block:
            return "".join(child["text"] for child in block["children"] if "text" in child)
        return block.get("text", "")
    return ""

def markdown_view(request, article_id):
    """
    Django API view to return a structured Markdown AST JSON.
    :param request: Django request object
    :param article_id: Article ID
    :return: JSONResponse with nested JSON structure
    """
    if article_id == 0:  # Special case: Load test.md instead of database content
        ast = parse_markdown(file_path=os.path.join(BASE_DIR, "test.md"))
    else:
        article = get_object_or_404(Article, id=article_id)
        ast = parse_markdown(article.content)

    structured_data = build_nested_structure(ast)
    return JsonResponse(structured_data, json_dumps_params={"ensure_ascii": False, "indent": 2})

def home(request):
    """
    Homepage view with a simple welcome message.
    """
    return HttpResponse("Welcome to CodeScribe!")
