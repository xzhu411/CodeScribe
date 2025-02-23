import mistune
import json
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import Article
from llm_core.api import CoreLLM  # Ensure correct import of CoreLLM
from llm_core.utils import traverse_directory

# Get the current directory path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize the LLM model
llm = CoreLLM(verbose=False)
llm.load_model("Gemini 2.0 Flash")  # You can replace this with your own LLM

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

def replace_code_with_model_output(nested_dict, return_type="md"):
    """
    Traverse the nested structure and replace Python code with model-generated content.
    """
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            replace_code_with_model_output(value)
        elif isinstance(value, str):
            print("Sending code to LLM for generation...")  # Debug log
            generated_md = llm(value)  # Let CoreLLM generate new Markdown
            if return_type == "md":
                nested_dict[key] = generated_md
            else:
                nested_dict[key] = extract_text(generated_md)


def markdown_view(request, article_id):
    """
    Django API view to return a structured Markdown AST JSON.
    """
    if request.method == "POST" and request.FILES:
        uploaded_file = request.FILES["file"]
        # Get the first input file dir
        root_dir = request.FILES.getlist("file")[0].name
    
    # if article_id == 0:
    #     root_dir = parse_markdown(file_path=os.path.join(BASE_DIR, "test.md"))
    # else:
    #     article = get_object_or_404(Article, id=article_id)
    #     root_dir = parse_markdown(article.content)

    structured_data = traverse_directory(root_dir)
    replace_code_with_model_output(structured_data)
    
    return JsonResponse(structured_data, json_dumps_params={"ensure_ascii": False, "indent": 2})



def home(request):
    """
    Homepage view with a simple welcome message.
    """
    return HttpResponse("Welcome to CodeScribe!")
