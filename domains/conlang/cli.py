"""
CLI commands for the conlang domain.
"""
import argparse
import json
import os
from typing import Dict, Any, List

from .. import get_domain_processor

def register_commands(subparsers) -> None:
    """
    Register conlang-specific commands with the main CLI.
    
    Args:
        subparsers: The argparse subparsers object to register commands with
    """
    # words command: List, search, and manage words
    words_parser = subparsers.add_parser("words", help="Manage conlang words")
    words_subparsers = words_parser.add_subparsers(dest="words_command", required=True)
    
    # words list command
    list_parser = words_subparsers.add_parser("list", help="List words")
    list_parser.add_argument("--part-of-speech", type=str, help="Filter by part of speech")
    list_parser.add_argument("--origin-language", type=str, help="Filter by origin language")
    list_parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    
    # words get command
    get_parser = words_subparsers.add_parser("get", help="Get word details")
    get_parser.add_argument("id", type=str, help="Word ID")
    
    # words create command
    create_parser = words_subparsers.add_parser("create", help="Create a word")
    create_parser.add_argument("--file", type=str, required=True, help="JSON file with word data")
    
    # words update command
    update_parser = words_subparsers.add_parser("update", help="Update a word")
    update_parser.add_argument("id", type=str, help="Word ID")
    update_parser.add_argument("--field", type=str, required=True, help="Field to update")
    update_parser.add_argument("--value", type=str, required=True, help="New value")
    
    # words delete command
    delete_parser = words_subparsers.add_parser("delete", help="Delete a word")
    delete_parser.add_argument("id", type=str, help="Word ID")
    
    # words search command
    search_parser = words_subparsers.add_parser("search", help="Search for words")
    search_parser.add_argument("--english", type=str, help="Search in English translations")
    search_parser.add_argument("--eldorian", type=str, help="Search in Eldorian words")
    search_parser.add_argument("--part-of-speech", type=str, help="Filter by part of speech")
    
    # statistics command
    stats_parser = words_subparsers.add_parser("stats", help="Get lexicon statistics")

def handle_command(args) -> None:
    """
    Handle conlang-specific commands.
    
    Args:
        args: The parsed command-line arguments
    """
    if not hasattr(args, 'words_command'):
        return
    
    # Get the conlang domain processor
    processor = get_domain_processor("conlang")
    
    if args.words_command == "list":
        criteria = {}
        if args.part_of_speech:
            criteria["part_of_speech"] = args.part_of_speech
        if args.origin_language:
            criteria["origin_language"] = args.origin_language
            
        words = processor.search_words(criteria)
        _display_words(words, args.format)
        
    elif args.words_command == "get":
        word = processor.get_entry(args.id)
        if word:
            print(json.dumps(word, indent=2))
        else:
            print(f"Word with ID '{args.id}' not found")
            
    elif args.words_command == "create":
        with open(args.file, "r") as f:
            word_data = json.load(f)
        
        word_id = processor.create_entry(word_data)
        print(f"Created word with ID: {word_id}")
        
    elif args.words_command == "update":
        # Parse field path and value
        field_parts = args.field.split(".")
        
        # Build nested update dictionary
        update_data = {}
        current = update_data
        for part in field_parts[:-1]:
            current[part] = {}
            current = current[part]
        
        # Set the leaf value
        current[field_parts[-1]] = args.value
        
        result = processor.update_entry(args.id, update_data)
        if result:
            print(f"Updated word {args.id}")
        else:
            print(f"Failed to update word {args.id}")
            
    elif args.words_command == "delete":
        if processor.delete_entry(args.id):
            print(f"Deleted word {args.id}")
        else:
            print(f"Failed to delete word {args.id}")
            
    elif args.words_command == "search":
        criteria = {}
        if args.english:
            criteria["english_contains"] = args.english
        if args.eldorian:
            criteria["eldorian_contains"] = args.eldorian
        if args.part_of_speech:
            criteria["part_of_speech"] = args.part_of_speech
            
        words = processor.search_words(criteria)
        _display_words(words, "table")
        
    elif args.words_command == "stats":
        all_words = processor.repository.get_all_entries()
        
        # Count by part of speech
        pos_counts = {}
        for word in all_words:
            pos = word.get("core", {}).get("part_of_speech", "unknown")
            pos_counts[pos] = pos_counts.get(pos, 0) + 1
        
        # Count by origin language
        origin_counts = {}
        for word in all_words:
            for origin in word.get("etymology", {}).get("origin_words", []):
                lang = origin.get("language", "unknown")
                origin_counts[lang] = origin_counts.get(lang, 0) + 1
        
        # Display statistics
        print(f"Total words: {len(all_words)}")
        print("\nBy part of speech:")
        for pos, count in pos_counts.items():
            print(f"  {pos}: {count}")
        print("\nBy origin language:")
        for lang, count in origin_counts.items():
            print(f"  {lang}: {count}")

def _display_words(words: List[Dict[str, Any]], format_type: str = "table") -> None:
    """
    Display a list of words in the specified format.
    
    Args:
        words: The list of words to display
        format_type: The format to use ("table" or "json")
    """
    if format_type == "json":
        print(json.dumps(words, indent=2))
    else:
        # Table format
        if not words:
            print("No words found")
            return
            
        # Print header
        print(f"{'ID':<15} {'ELDORIAN':<20} {'ENGLISH':<20} {'PART OF SPEECH':<15}")
        print("-" * 70)
        
        # Print each word
        for word in words:
            word_id = word.get("id", "")[:12]
            eldorian = word.get("eldorian", "")[:18]
            english = word.get("english", "")[:18]
            pos = word.get("core", {}).get("part_of_speech", "")[:13]
            
            print(f"{word_id:<15} {eldorian:<20} {english:<20} {pos:<15}")
