import os
from openai import OpenAI
from langchain_core.prompts import PromptTemplate

from config import OPENAI_API_KEY  # Import centralized config

def execute_prompt_step(step_config, context):
    # Load template and inject dynamic values
    with open(step_config["template"], "r") as file:
        template_text = file.read()
    # Prepare inputs: resolve parameters based on provided keys
    input_vars = {key: context.get(val.strip("{}"), val) for key, val in step_config.get("parameters", {}).items()}
    prompt = PromptTemplate(template=template_text, input_variables=list(input_vars.keys()))
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Use the OpenAI ChatCompletion API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt.format(**input_vars)}]
    )
    return response.choices[0].message.content
