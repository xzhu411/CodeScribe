from transformers import pipeline

# Load a small LLM model from Hugging Face
# print("Loading model...")
llm = pipeline("text2text-generation", model="google/flan-t5-small")
# print("Model loaded successfully.")

def generate_markdown(command: str) -> str:
    """
    Generate a Markdown string based on user command using an LLM.
    """
    print(f"Received command: {command}")  # Debugging log

    if not command:
        return "# Error\nCommand cannot be empty."

    # Generate text using the LLM
    response = llm(command, max_length=200, truncation=True)
    generated_text = response[0]['generated_text']

    # Format as Markdown
    markdown_output = f"# Generated Response\n\n{generated_text}\n"

    print(f"Generated Markdown:\n{markdown_output}")  # Debugging log
    return markdown_output

# Test the model
# if __name__ == "__main__":
#     test_command = "Summarize the importance of AI in 3 sentences."
#     print("Running test command...")
#     md_result = generate_markdown(test_command)
#     print("Test complete. Output:")
#     print(md_result)
