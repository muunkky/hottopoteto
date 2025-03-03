import re
import logging

def resolve_parameters(step, context):
    # Convert Pydantic model to dict if needed
    step_config = step.dict() if hasattr(step, "dict") else step.copy()
    logging.info(f"Resolving parameters for step: {step_config.get('name')}")
    logging.info(f"Current context: {context}")
    
    # Special case for extracting category from LLM output
    if "Step1_output.category" in str(step_config):
        # Try to extract category from the text
        llm_output = context.get("Step_1:_Initialization_output", "")
        logging.info(f"Extracting category from LLM output: {llm_output}")
        
        category_match = re.search(r"Category:\s*(\w+)", llm_output)
        if category_match:
            extracted_category = category_match.group(1)
            context["Step1_output.category"] = extracted_category
            logging.info(f"Extracted category: {extracted_category}")
        else:
            logging.warning(f"No category found in LLM output")
    
    def replace_placeholder(match):
        key = match.group(1).strip()
        value = str(context.get(key, match.group(0)))
        logging.info(f"Replacing placeholder {key} with value: {value}")
        return value
    
    # Replace placeholders in all string values
    for key, value in step_config.items():
        if isinstance(value, str):
            original = value
            step_config[key] = re.sub(r"{{(.*?)}}", replace_placeholder, value)
            if original != step_config[key]:
                logging.info(f"Parameter '{key}' changed from '{original}' to '{step_config[key]}'")
    
    return step_config