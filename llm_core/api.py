# Make LLM callable in API style
# <input>: root file directory of raw code
# <output>: html file of code file documentation

import os
import markdownify
from dotenv import load_dotenv

class CoreLLM:
    def __init__(self, verbose:bool=False):
        # Choose model
        self.model_name = None
        self.client = None
        self.tokenizer = None
        load_dotenv("llm_core\.env")
        self.verbose = verbose

        with open("llm_core\prompt.txt", "r", encoding="utf-8") as file:
            self.prompt_template = file.read().strip()  # Read and strip extra whitespace

    def load_model(self, model_name:str):
        self.model_name = model_name
        match self.model_name:
            case "meta-llama/Llama-3.2-3B-Instruct":
                from transformers import AutoModelForCausalLM, AutoTokenizer
                # Load the fine-tuned model with 4-bit quantization
                self.client = AutoModelForCausalLM.from_pretrained(
                    os.getenv("LOCAL_MODELS")["meta-llama/Llama-3.2-3B-Instruct"], load_in_4bit=True, device_map="auto"
                )

                # Verify the model is loaded in 4-bit
                if self.verbose:
                    print(self.client)

                # Load the tokenizer to interact with the model
                self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", token=os.getenv("HUGGINGFACE_TOKEN"))

            case "Gemini 2.0 Flash":
                from google import genai
                self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def gemini_call(self, content:str):
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=content,
        )
        return response.text
    
    def local_quantized_call(self, content:str):
        inputs = self.tokenizer(content, return_tensors="pt")

        # Move inputs to the same device as the model
        device = self.client.device  # Get the device where the model is loaded
        inputs = {key: value.to(device) for key, value in inputs.items()}  # Move input tensors to the same device

        # Generate output from the model
        outputs = self.client.generate(**inputs)

        # Decode the output
        decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return decoded_output
    
    @staticmethod
    def html2markdown(response:str):
        markdown_response = markdownify.markdownify(response, heading_style="ATX")  # Convert HTML to Markdown

        return markdown_response


    def __call__(self, user_content:str):
        content = self.prompt_template.format(user_content)
        match self.model_name:
            case "Gemini 2.0 Flash":
                return self.html2markdown(self.gemini_call(content))
            case _:
                return self.html2markdown(self.local_quantized_call(content))


# Models: Qwen/Qwen2.5-3B-Instruct； meta-llama/Llama-3.2-3B-Instruct
# dsets: philschmid/markdown-documentation-transformers， 


# Test
# # Initialize the CoreLLM with verbose mode
# core_llm = CoreLLM(verbose=False)

# # Load the Gemini 2.0 Flash model
# core_llm.load_model("Gemini 2.0 Flash")

# # Define a simple "hello" prompt to test the model
# hello_prompt = "Hello, how are you today?"

# # Call the model with the prompt and get the response
# response = core_llm(hello_prompt)

# # Print the response
# print(response)