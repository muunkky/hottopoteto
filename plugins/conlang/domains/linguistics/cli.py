"""
CLI commands for linguistics domain
"""
import click
import logging
from typing import Dict, Any
from core.cli.utils import format_output

logger = logging.getLogger(__name__)

def register_commands(subparsers):
    """Register domain-specific commands with the CLI"""
    linguistics_parser = subparsers.add_parser("linguistics", help="Linguistics domain commands")
    linguistics_subparsers = linguistics_parser.add_subparsers(dest="linguistics_command", required=True)
    
    # Add word-related commands
    word_parser = linguistics_subparsers.add_parser("word", help="Word management commands")
    word_subparsers = word_parser.add_subparsers(dest="word_command", required=True)
    
    # Add word search command
    search_parser = word_subparsers.add_parser("search", help="Search for words")
    search_parser.add_argument("--language", type=str, help="Language code")
    search_parser.add_argument("--pattern", type=str, help="Search pattern")
    
    # Add language commands
    language_parser = linguistics_subparsers.add_parser("language", help="Language management commands")
    language_subparsers = language_parser.add_subparsers(dest="language_command", required=True)
    
    # Add language list command
    list_parser = language_subparsers.add_parser("list", help="List languages")

def handle_command(args):
    """Handle domain-specific commands"""
    if not hasattr(args, "linguistics_command"):
        return False
        
    if args.linguistics_command == "word":
        if args.word_command == "search":
            search_words(args.language, args.pattern)
            return True
    
    if args.linguistics_command == "language":
        if args.language_command == "list":
            list_languages()
            return True
    
    return False

def search_words(language=None, pattern=None):
    """Search for words in the database"""
    from .functions import search_words_function
    
    try:
        result = search_words_function(language=language, pattern=pattern)
        format_output(result)
    except Exception as e:
        logger.error(f"Error searching words: {e}")
        print(f"Error: {e}")

def list_languages():
    """List available languages"""
    from .functions import list_languages_function
    
    try:
        result = list_languages_function()
        format_output(result)
    except Exception as e:
        logger.error(f"Error listing languages: {e}")
        print(f"Error: {e}")
