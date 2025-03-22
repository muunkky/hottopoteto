"""
Functions for linguistics domain
"""
import logging
from typing import Dict, Any, List
from core.registration import register_domain_function
from .models import Word, Phoneme, MorphologicalRule

logger = logging.getLogger(__name__)

def analyze_word(word: str, language: str) -> Dict[str, Any]:
    """
    Analyze a word's linguistic properties
    
    Args:
        word: The word to analyze
        language: The language to use for analysis
        
    Returns:
        Dictionary of linguistic properties
    """
    # Example implementation
    return {
        "characters": len(word),
        "syllables": estimate_syllables(word),
        "language": language
    }

def estimate_syllables(word: str) -> int:
    """
    Estimate number of syllables in a word
    
    Args:
        word: The word to analyze
        
    Returns:
        Estimated syllable count
    """
    # Very basic syllable counting (not linguistically accurate)
    vowels = "aeiouAEIOU"
    count = 0
    prev_was_vowel = False
    
    for char in word:
        if char in vowels:
            if not prev_was_vowel:
                count += 1
            prev_was_vowel = True
        else:
            prev_was_vowel = False
            
    return max(count, 1)  # At least one syllable

def parse_phonemes(text: str, phoneme_inventory: List[Dict[str, Any]]) -> List[str]:
    """
    Parse text into constituent phonemes
    
    Args:
        text: Text to analyze
        phoneme_inventory: List of phonemes in the language
        
    Returns:
        List of phoneme symbols found in the text
    """
    # Example implementation
    result = []
    
    # Sort phonemes by length (longest first) to avoid partial matches
    sorted_phonemes = sorted(phoneme_inventory, key=lambda p: len(p["symbol"]), reverse=True)
    
    i = 0
    while i < len(text):
        matched = False
        for phoneme in sorted_phonemes:
            symbol = phoneme["symbol"]
            if text[i:i+len(symbol)] == symbol:
                result.append(symbol)
                i += len(symbol)
                matched = True
                break
        
        if not matched:
            # Skip unknown character
            i += 1
            
    return result

# Register domain functions
register_domain_function("linguistics", "analyze_word", analyze_word)
register_domain_function("linguistics", "estimate_syllables", estimate_syllables)
register_domain_function("linguistics", "parse_phonemes", parse_phonemes)
