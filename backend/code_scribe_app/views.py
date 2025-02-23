import json
import os
import sys
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from llm_core.api import CoreLLM  # Import CoreLLM model
from llm_core.utils import traverse_directory  # Import function to extract code files

# Initialize CoreLLM
core_llm = CoreLLM(verbose=False)
core_llm.load_model("Gemini 2.0 Flash")  # You can change the model here

def process_code_files(directory_structure):
    """
    Recursively process directory structure and replace code files with their Markdown versions.
    """
    if isinstance(directory_structure, dict):
        updated_structure = {}
        for key, value in directory_structure.items():
            updated_structure[key] = process_code_files(value)  # Recursively process subdirectories
        return updated_structure
    elif isinstance(directory_structure, str):
        # If it's a string, it's code content, so process it with LLM
        markdown_response = core_llm(directory_structure)
        return markdown_response
    else:
        return directory_structure  # If None or unknown type, return as-is

@csrf_exempt
def generate_markdown_from_directory(request):
    """Handles API request, retrieves directory structure, processes code, and returns Markdown."""
    
    if request.method == "POST":
        try:
            # Parse JSON request
            data = json.loads(request.body)
            directory_path = data.get("directory_path", "").strip()

            if not directory_path:
                return JsonResponse({"status": "error", "message": "Directory path cannot be empty"}, status=400)
            
            if not os.path.exists(directory_path):
                return JsonResponse({"status": "error", "message": "Directory does not exist"}, status=400)
            
            # Extract code structure as a formatted dictionary
            directory_structure = json.loads(traverse_directory(directory_path))

            if not directory_structure:
                return JsonResponse({"status": "error", "message": "No valid code found in directory"}, status=400)

            # Process the extracted code files and convert them into Markdown
            markdown_structure = process_code_files(directory_structure)

            return JsonResponse({
                "status": "success",
                "message": "Generated markdown successfully",
                "data": markdown_structure
            })

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


# Home Page
def home(request):
    return HttpResponse("Welcome to CodeScribe!")
