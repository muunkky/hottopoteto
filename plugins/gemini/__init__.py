from core.schemas import register_schema
from .schemas.model_params import GENERATION_PARAMS_SCHEMA

# Register plugin schemas
register_schema("gemini.generation_params", GENERATION_PARAMS_SCHEMA)
