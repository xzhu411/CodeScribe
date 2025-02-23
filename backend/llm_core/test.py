# import llm_core
from api import CoreLLM

# Test
# # Initialize the CoreLLM with verbose mode
core_llm = CoreLLM(verbose=False)

# # Load the Gemini 2.0 Flash model
core_llm.load_model("Gemini 2.0 Flash")

# # Define a simple "hello" prompt to test the model
hello_prompt = "Hello, how are you today?"

# # Call the model with the prompt and get the response
response = core_llm(hello_prompt)

# # Print the response
print(response)