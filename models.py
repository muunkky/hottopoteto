from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Step(BaseModel):
    name: str
    type: str
    # For a prompt step, reference a template file.
    template: Optional[str] = None
    # For SQL steps, reference a query file.
    query: Optional[str] = None
    # For agent steps, reference a function file.
    function: Optional[str] = None
    # Parameters to be injected into the prompt or query.
    parameters: Dict[str, str] = Field(default_factory=dict)
    # Expected output format (e.g., "text", "json").
    output_format: str
    # Optional token limit for the LLM response.
    token_limit: Optional[int] = None
    # Optional database configuration file reference for SQL steps.
    db_config: Optional[str] = None

class Recipe(BaseModel):
    steps: List[Step]
