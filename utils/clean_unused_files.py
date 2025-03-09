import os
import re
import sys
from typing import Set, List, Dict, Tuple
import importlib
import ast
import logging
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

class ImportVisitor(ast.NodeVisitor):
    """AST visitor that collects all imports in a Python file."""
    
    def __init__(self):
        self.imports = set()
        self.from_imports = set()
        
    def visit_Import(self, node):
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        if node.module:  # 'from x import y' (node.module = x)
            self.from_imports.add(node.module)
        self.generic_visit(node)

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in a directory (recursive)."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def normalize_import_to_path(import_name: str, base_dir: str) -> str:
    """Convert an import statement to a file path."""
    # Replace dots with path separators
    path = import_name.replace(".", os.path.sep)
    # Check if it's a direct file import or package import
    if os.path.exists(os.path.join(base_dir, path + ".py")):
        return os.path.join(base_dir, path + ".py")
    elif os.path.exists(os.path.join(base_dir, path, "__init__.py")):
        return os.path.join(base_dir, path, "__init__.py")
    return None

def get_file_imports(filepath: str) -> Tuple[Set[str], Set[str]]:
    """Get all imports in a Python file using AST."""
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
            visitor = ImportVisitor()
            visitor.visit(tree)
            return visitor.imports, visitor.from_imports
        except SyntaxError:
            logging.warning(f"Syntax error in {filepath}, skipping...")
            return set(), set()

def find_all_project_files(directory: str, file_types: List[str]) -> Dict[str, List[str]]:
    """Find all files of specified types in a directory (recursive)."""
    files_by_type = {ext: [] for ext in file_types}
    
    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in file_types:
                files_by_type[ext].append(os.path.join(root, file))
    
    return files_by_type

def find_template_references(project_dir: str) -> Set[str]:
    """Find all prompt template references in YAML files and Python files."""
    referenced_templates = set()
    
    # Look for references in YAML files
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(('.yaml', '.yml')):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Look for template: "filename.txt" patterns
                        matches = re.findall(r'template:\s*["\']([^"\']+\.txt)["\']', content)
                        for match in matches:
                            referenced_templates.add(match)
                except:
                    pass
    
    # Look for references in Python files
    python_files = find_python_files(project_dir)
    for filepath in python_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for template paths in string literals
                matches = re.findall(r'["\']([^"\']*\.txt)["\']', content)
                for match in matches:
                    if match.endswith('.txt'):
                        referenced_templates.add(match)
        except:
            pass
    
    return referenced_templates

def find_unused_templates(project_dir: str) -> List[str]:
    """Find potentially unused template files."""
    # Get all .txt files
    txt_files = []
    prompt_dir = os.path.join(project_dir, 'prompts')
    
    if os.path.exists(prompt_dir):
        for root, _, files in os.walk(prompt_dir):
            for file in files:
                if file.endswith('.txt'):
                    txt_files.append(os.path.join(root, file))
    
    # Get all referenced templates
    referenced_templates = find_template_references(project_dir)
    
    # Find unused templates
    unused_templates = []
    for filepath in txt_files:
        filename = os.path.basename(filepath)
        rel_path = os.path.relpath(filepath, project_dir)
        
        # Check if this template is referenced
        if filename not in referenced_templates and rel_path not in referenced_templates:
            unused_templates.append(filepath)
    
    return unused_templates

def find_unused_files(project_dir: str) -> List[str]:
    """Find potentially unused Python files in a project."""
    # Step 1: Get all Python files in the project
    all_python_files = find_python_files(project_dir)
    
    # Create relative paths for easier comparison
    all_python_modules = {os.path.relpath(f, project_dir).replace(os.path.sep, ".")[:-3] 
                          for f in all_python_files}
    
    # Step 2: Track which files are imported
    imported_files = set()
    file_to_imports = {}
    
    for filepath in all_python_files:
        imports, from_imports = get_file_imports(filepath)
        file_to_imports[filepath] = (imports, from_imports)
        
        # Add to imported_files set
        for imp in imports:
            if imp in all_python_modules:
                imported_files.add(imp)
        
        for imp in from_imports:
            if imp in all_python_modules:
                imported_files.add(imp)
            # Handle cases like "from x.y import z"
            parts = imp.split(".")
            for i in range(len(parts)):
                module = ".".join(parts[:i+1])
                if module in all_python_modules:
                    imported_files.add(module)
    
    # Step 3: Check which files are directly used in recipe YAML files
    yaml_files = []
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith((".yaml", ".yml")):
                yaml_files.append(os.path.join(root, file))
    
    # Step 4: Special handling for entry points and imports in non-Python files
    special_files = {
        "main.py",  # Main entry point
        "__main__.py",  # Package entry point
        "__init__.py",  # Package initializers
        "setup.py",  # Installation script
        "conftest.py",  # Pytest fixtures
    }
    
    # Step 5: Convert Python modules to file paths
    imported_file_paths = set()
    for mod in imported_files:
        path = normalize_import_to_path(mod, project_dir)
        if path:
            imported_file_paths.add(path)
    
    # Step 6: Find unused files
    unused_files = []
    for filepath in all_python_files:
        rel_path = os.path.relpath(filepath, project_dir)
        module_name = rel_path.replace(os.path.sep, ".")[:-3]
        
        # Skip files that are imported
        if module_name in imported_files:
            continue
        
        # Skip files that are directly imported
        if filepath in imported_file_paths:
            continue
        
        # Skip special files
        filename = os.path.basename(filepath)
        if filename in special_files:
            continue
            
        # This file might be unused
        unused_files.append(filepath)
    
    return unused_files

def analyze_file_usage(project_dir: str) -> Dict[str, List[str]]:
    """Analyze file usage and categorize files."""
    all_python_files = find_python_files(project_dir)
    unused_files = find_unused_files(project_dir)
    
    # Group files by directory for better organization
    files_by_directory = {}
    
    for filepath in all_python_files:
        directory = os.path.dirname(filepath)
        rel_dir = os.path.relpath(directory, project_dir)
        
        if rel_dir not in files_by_directory:
            files_by_directory[rel_dir] = {
                "used": [],
                "unused": []
            }
            
        if filepath in unused_files:
            files_by_directory[rel_dir]["unused"].append(os.path.basename(filepath))
        else:
            files_by_directory[rel_dir]["used"].append(os.path.basename(filepath))
    
    return files_by_directory

def print_usage_analysis(usage_by_dir: Dict[str, Dict[str, List[str]]]):
    """Print the usage analysis in a readable format."""
    print("\n==== File Usage Analysis ====\n")
    
    for directory, files in sorted(usage_by_dir.items()):
        if directory == '.':
            print("Root Directory:")
        else:
            print(f"Directory: {directory}/")
            
        if files["used"]:
            print("  Used Files:")
            for file in sorted(files["used"]):
                print(f"    [OK] {file}")
                
        if files["unused"]:
            print("  Potentially Unused Files:")
            for file in sorted(files["unused"]):
                print(f"    [X] {file}")
        print()
        
def print_cleanup_suggestions(unused_files: List[str], project_dir: str):
    """Print suggestions for cleanup."""
    print("\n==== Cleanup Suggestions ====\n")
    
    # List the potentially unused files
    print(f"Found {len(unused_files)} potentially unused files:")
    
    for filepath in sorted(unused_files):
        rel_path = os.path.relpath(filepath, project_dir)
        print(f"  - {rel_path}")
    
    # Generate cleanup commands
    if unused_files:
        print("\nTo review these files:")
        for filepath in sorted(unused_files)[:5]:  # Show first few
            rel_path = os.path.relpath(filepath, project_dir)
            print(f"  cat '{rel_path}'")
            
        print("\nTo move these files to a backup directory:")
        print("  mkdir -p backup_unused")
        for filepath in sorted(unused_files)[:5]:
            rel_path = os.path.relpath(filepath, project_dir)
            backup_path = os.path.join("backup_unused", rel_path)
            backup_dir = os.path.dirname(backup_path)
            print(f"  mkdir -p '{backup_dir}'")
            print(f"  mv '{rel_path}' '{backup_path}'")
            
        if len(unused_files) > 5:
            print(f"  ... and {len(unused_files) - 5} more files")
            
        print("\nTo delete these files (be cautious!):")
        for filepath in sorted(unused_files)[:5]:
            rel_path = os.path.relpath(filepath, project_dir)
            print(f"  rm '{rel_path}'")
            
        if len(unused_files) > 5:
            print(f"  ... and {len(unused_files) - 5} more files")
    
    print("\nNOTE: This analysis may have false positives. Always check files before deleting them.")

if __name__ == "__main__":
    # Allow specifying the project directory as an argument
    project_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"Analyzing files in: {project_dir}")
    
    try:
        # Find unused Python files
        unused_files = find_unused_files(project_dir)
        
        # Find unused template files
        unused_templates = find_unused_templates(project_dir)
        
        # Combine the lists
        all_unused_files = unused_files + unused_templates
        
        # Get detailed analysis
        usage_by_directory = analyze_file_usage(project_dir)
        
        # Add template analysis
        prompt_dir_rel = os.path.relpath(os.path.join(project_dir, 'prompts'), project_dir)
        if os.path.exists(os.path.join(project_dir, 'prompts')):
            if prompt_dir_rel not in usage_by_directory:
                usage_by_directory[prompt_dir_rel] = {"used": [], "unused": []}
            
            for template in unused_templates:
                usage_by_directory[prompt_dir_rel]["unused"].append(os.path.basename(template))
        
        # Print results
        print_usage_analysis(usage_by_directory)
        print_cleanup_suggestions(all_unused_files, project_dir)
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
