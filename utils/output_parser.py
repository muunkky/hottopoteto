# utils/output_parser.py
from langchain.output_parsers import BaseOutputParser
import json

class JSONOutputParser(BaseOutputParser):
    def parse(self, text: str):
        """
        Parse output text into a JSON object.
        
        Args:
            text (str): The raw text output from a chain.
        
        Returns:
            dict: Parsed JSON data.
        """
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse output as JSON.")

def parse_output(output: str, output_format: str):
    """
    Parse the output based on the expected output format.
    
    Args:
        output (str): The raw output from a chain.
        output_format (str): Expected format ("json", "text", etc.)
    
    Returns:
        The parsed output in the specified format.
    """
    if output_format.lower() == "json":
        parser = JSONOutputParser()
        return parser.parse(output)
    # For 'text' or other formats, return the raw output or implement further parsing
    return output
# Compare this snippet from chains/sequential_chain.py: