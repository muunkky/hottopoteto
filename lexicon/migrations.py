from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def migrate_word(word_entry: Dict, target_version: str) -> Dict:
    """
    Migrate a word entry to a newer schema version.
    Returns the migrated word entry.
    """
    current_version = word_entry.get("metadata", {}).get("schema_version", "1.0")
    
    if current_version == target_version:
        return word_entry
        
    logger.info(f"Migrating word {word_entry.get('word_id')} from v{current_version} to v{target_version}")
    
    # Clone to avoid modifying the original
    migrated = dict(word_entry)
    
    # Apply migrations in sequence
    if current_version == "1.0" and (target_version == "1.1" or target_version > "1.0"):
        migrated = _migrate_1_0_to_1_1(migrated)
        current_version = "1.1"
        
    if current_version == "1.1" and (target_version == "1.2" or target_version > "1.1"):
        migrated = _migrate_1_1_to_1_2(migrated)
        current_version = "1.2"
        
    # ... add more migrations as needed
    
    # Update metadata
    if "metadata" not in migrated:
        migrated["metadata"] = {}
    migrated["metadata"]["schema_version"] = target_version
    migrated["metadata"]["updated_at"] = datetime.now().isoformat()
    
    return migrated

def _migrate_1_0_to_1_1(word_entry: Dict) -> Dict:
    """Migrate from schema v1.0 to v1.1"""
    # Example migration: Add usage_examples field
    migrated = dict(word_entry)
    
    # Add usage examples field if not present
    if "usage_examples" not in migrated:
        migrated["usage_examples"] = []
        
    # Ensure core section has definitions
    if "core" in migrated and "definitions" not in migrated["core"]:
        migrated["core"]["definitions"] = [
            {
                "meaning": migrated.get("english", ""),
                "domain": "general",
                "register": "standard",
                "examples": []
            }
        ]
    
    return migrated

def _migrate_1_1_to_1_2(word_entry: Dict) -> Dict:
    """Migrate from schema v1.1 to v1.2"""
    # Example: Add cultural_notes field
    migrated = dict(word_entry)
    migrated["cultural_notes"] = []
    return migrated