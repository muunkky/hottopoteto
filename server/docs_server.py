import json
import os
import yaml
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="LangChain Recipe Documentation")

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
static_dir = os.path.join(current_dir, "static")
templates_dir = os.path.join(current_dir, "templates")

# Create directories if they don't exist
os.makedirs(static_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)

# Setup templates and static
templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Convert JSON Schema to OpenAPI
schema_path = os.path.join(project_root, "schema", "recipe_schema.json")
with open(schema_path, "r") as f:
    json_schema = json.load(f)

# Create an OpenAPI spec
openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "LangChain Recipe Schema",
        "description": "Documentation for LangChain Recipe format",
        "version": "1.0.0"
    },
    "paths": {},
    "components": {
        "schemas": {
            "Recipe": json_schema
        }
    }
}

# Save the OpenAPI spec
openapi_path = os.path.join(static_dir, "openapi.json")
with open(openapi_path, "w") as f:
    json.dump(openapi_spec, f, indent=2)

# Create Swagger UI HTML file
swagger_html = """
<!DOCTYPE html>
<html>
<head>
    <title>LangChain Recipe Documentation</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.1.0/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.1.0/swagger-ui-bundle.js"></script>
    <script>
        const ui = SwaggerUIBundle({
            url: "/static/openapi.json",
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            deepLinking: true,
        })
    </script>
</body>
</html>
"""

# Save the Swagger UI HTML
swagger_path = os.path.join(templates_dir, "swagger.html")
with open(swagger_path, "w") as f:
    f.write(swagger_html)

@app.get("/", response_class=HTMLResponse)
async def get_docs(request: Request):
    return templates.TemplateResponse("swagger.html", {"request": request})

@app.get("/schema", response_class=HTMLResponse)
async def get_schema():
    with open(schema_path, "r") as f:
        return json.dumps(json.load(f), indent=2)

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
