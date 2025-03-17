from typing import Dict, List, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

def update_indices(entry: Dict, indices_dir: str) -> None:
    """Update indices with a new or updated entry"""
    # Ensure directory exists
    os.makedirs(indices_dir, exist_ok=True)
    
    # Extract properties to index - make this completely generic
    # instead of hardcoding fields like "english", "part_of_speech", etc.
    properties = _extract_indexable_properties(entry)
    
    # Update each property index
    for prop_name, values in properties.items():
        index_file = os.path.join(indices_dir, f"by_{prop_name}.json")
        index_data = load_index(index_file)
        
        # Add entry ID to each value
        entry_id = entry.get("id")
        if not entry_id:
            logger.warning("Entry has no ID, skipping indexing")
            continue
            
        for value in values:
            value_key = str(value).lower()  # Convert to string and lowercase
            if value_key not in index_data:
                index_data[value_key] = []
            if entry_id not in index_data[value_key]:
                index_data[value_key].append(entry_id)
        
        # Save updated index
        save_index(index_data, index_file)

def _extract_indexable_properties(entry: Dict) -> Dict[str, List]:
    """Extract indexable properties from an entry"""
    properties = {}
    
    # Flatten all properties for indexing
    def extract_props(data, prefix=""):
        if isinstance(data, dict):
            for key, value in data.items():
                prop_path = f"{prefix}_{key}" if prefix else key
                
                # Don't index very complex nested structures
                if isinstance(value, (str, int, float, bool)):
                    if prop_path not in properties:
                        properties[prop_path] = []
                    properties[prop_path].append(value)
                    
                # Also index ID fields specially
                if key.endswith("_id") or key == "id":
                    if "id" not in properties:
                        properties["id"] = []
                    properties["id"].append(value)
                    
                # Recurse into nested structures
                extract_props(value, prop_path)
                
        elif isinstance(data, list):
            # For lists, add each value separately
            for item in data:
                if isinstance(item, (str, int, float, bool)):
                    if prefix not in properties:
                        properties[prefix] = []
                    properties[prefix].append(item)
                else:
                    extract_props(item, prefix)
    
    extract_props(entry)
    return properties

def load_index(index_path: str) -> Dict:
    """Load an index file, or return empty dict if it doesn't exist"""
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading index {index_path}: {e}")
            return {}
    return {}

def save_index(index_data: Dict, index_path: str) -> None:
    """Save an index file"""
    try:
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving index {index_path}: {e}")

def search_by_criteria(criteria: Dict, storage_dir: str) -> List[Dict]:
    """
    Search for entries matching specific criteria.
    This is a generic implementation that works with any properties.
    """
    indices_dir = os.path.join(storage_dir, "indices")
    entries_dir = os.path.join(storage_dir, "entries")
    candidates = set()
    first_filter = True
    
    # For each criterion, find matching entries
    for prop, value in criteria.items():
        # Handle special case for text search
        if prop.endswith("_contains"):
            base_prop = prop.replace("_contains", "")
            index_path = os.path.join(indices_dir, f"by_{base_prop}.json")
            if not os.path.exists(index_path):
                # If no index exists for this property, skip this criterion
                continue
                
            with open(index_path) as f:
                prop_index = json.load(f)
            
            # Find entries where property contains the search value
            matches = set()
            search_text = str(value).lower()
            for indexed_val, entry_ids in prop_index.items():
                if search_text in indexed_val.lower():
                    matches.update(entry_ids)
        else:
            # Direct property match
            index_path = os.path.join(indices_dir, f"by_{prop}.json")
            if not os.path.exists(index_path):
                continue
                
            with open(index_path) as f:
                prop_index = json.load(f)
            
            # Find entries with exact property match
            value_key = str(value).lower()
            matches = set(prop_index.get(value_key, []))
        
        # Intersect with previous results if not first filter
        if first_filter:
            candidates = matches
            first_filter = False
        else:
            candidates = candidates.intersection(matches)
            
        # If no candidates remain, return empty list
        if not candidates:
            return []
    
    # If no filters applied, get all entries
    if first_filter:
        for filename in os.listdir(entries_dir):
            if filename.endswith('.json'):
                entry_id = filename.replace('.json', '')
                candidates.add(entry_id)
    
    # Load the candidate entries
    results = []
    for entry_id in candidates:
        entry_path = os.path.join(entries_dir, f"{entry_id}.json")
        if os.path.exists(entry_path):
            try:
                with open(entry_path, 'r') as f:
                    entry_data = json.load(f)
                    results.append(entry_data)
            except Exception as e:
                logger.error(f"Error loading entry {entry_id}: {e}")
    
    return results
