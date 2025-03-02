# chains/prompt_chain.py
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def build_prompt_chain(step_config: dict) -> LLMChain:
    """
    Build an LLMChain for a 'prompt' step based on the given configuration.
    
    Args:
        step_config (dict): Dictionary containing the step configuration from YAML.
    
    Returns:
        LLMChain: A configured chain instance for LLM prompting.
    """
    # Load the prompt template from an external file
    with open(step_config["template"], "r") as file:
        template_text = file.read()

    # Create a PromptTemplate using the keys from 'parameters'
    input_vars = list(step_config.get("parameters", {}).keys())
    prompt = PromptTemplate(input_variables=input_vars, template=template_text)

    # Initialize the LLM (using environment variables for API key, etc.)
    llm = OpenAI(temperature=0.7)
    
    # Create and return the LLMChain
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain
