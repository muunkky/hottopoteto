from typing import Dict, List, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

def update_indices(word_entry: Dict, indices_dir: str) -> None:
    """Update all lexicon indices with the new or updated word entry"""
    # Ensure directories exist
    os.makedirs(indices_dir, exist_ok=True)
    
    # Update English index
    english_index = load_index(os.path.join(indices_dir, "by_english.json"))
    english = word_entry.get("english", "").lower()
    if english:
        if english not in english_index:
            english_index[english] = []
        if word_entry["word_id"] not in english_index[english]:
            english_index[english].append(word_entry["word_id"])
    save_index(english_index, os.path.join(indices_dir, "by_english.json"))
    
    # Update part of speech index
    pos_index = load_index(os.path.join(indices_dir, "by_part_of_speech.json"))
    pos = word_entry.get("core", {}).get("part_of_speech", "")
    if pos:
        if pos not in pos_index:
            pos_index[pos] = []
        if word_entry["word_id"] not in pos_index[pos]:
            pos_index[pos].append(word_entry["word_id"])
    save_index(pos_index, os.path.join(indices_dir, "by_part_of_speech.json"))
    
    # Update origin language index
    origin_lang_index = load_index(os.path.join(indices_dir, "by_origin_language.json"))
    for origin in word_entry.get("etymology", {}).get("origin_words", []):
        lang = origin.get("language", "")
        if lang:
            if lang not in origin_lang_index:
                origin_lang_index[lang] = []
            if word_entry["word_id"] not in origin_lang_index[lang]:
                origin_lang_index[lang].append(word_entry["word_id"])
    save_index(origin_lang_index, os.path.join(indices_dir, "by_origin_language.json"))
    
    # Update semantic domain index
    domain_index = load_index(os.path.join(indices_dir, "by_semantic_domain.json"))
    for definition in word_entry.get("core", {}).get("definitions", []):
        domain = definition.get("domain", "")
        if domain:
            if domain not in domain_index:
                domain_index[domain] = []
            if word_entry["word_id"] not in domain_index[domain]:
                domain_index[domain].append(word_entry["word_id"])
    save_index(domain_index, os.path.join(indices_dir, "by_semantic_domain.json"))

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

def search_by_criteria(criteria: Dict, lexicon_dir: str) -> List[Dict]:
    """
    Search for words matching specific criteria
    Returns a list of matching word entries
    """
    indices_dir = os.path.join(lexicon_dir, "indices")
    words_dir = os.path.join(lexicon_dir, "words")
    candidates = set()
    first_filter = True
    
    # Filter by English text
    if "english_contains" in criteria:
        english_index = load_index(os.path.join(indices_dir, "by_english.json"))
        english_matches = set()
        search_text = criteria["english_contains"].lower()
        
        for english, word_ids in english_index.items():
            if search_text in english.lower():
                english_matches.update(word_ids)
                
        if first_filter:
            candidates = english_matches
            first_filter = False
        else:
            candidates = candidates.intersection(english_matches)
            
        if not candidates:
            return []
    
    # Filter by part of speech
    if "part_of_speech" in criteria:
        pos_index = load_index(os.path.join(indices_dir, "by_part_of_speech.json"))
        pos_matches = set(pos_index.get(criteria["part_of_speech"], []))
        
        if first_filter:
            candidates = pos_matches
            first_filter = False
        else:
            candidates = candidates.intersection(pos_matches)
            
        if not candidates:
            return []
    
    # Filter by origin language
    if "origin_language" in criteria:
        origin_index = load_index(os.path.join(indices_dir, "by_origin_language.json"))
        origin_matches = set(origin_index.get(criteria["origin_language"], []))
        
        if first_filter:
            candidates = origin_matches
            first_filter = False
        else:
            candidates = candidates.intersection(origin_matches)
            
        if not candidates:
            return []
    
    # If no criteria were applied, get all words
    if first_filter:
        # Get all word IDs
        candidates = set()
        for filename in os.listdir(words_dir):
            if filename.endswith('.json'):
                word_id = filename.replace('.json', '')
                candidates.add(word_id)
    
    # Load the candidate word entries
    results = []
    for word_id in candidates:
        word_path = os.path.join(words_dir, f"{word_id}.json")
        if os.path.exists(word_path):
            try:
                with open(word_path, 'r') as f:
                    word_data = json.load(f)
                    results.append(word_data)
            except Exception as e:
                logger.error(f"Error loading word {word_id}: {e}")
    
    return results