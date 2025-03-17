# domains/conlang/processors.py
def create_grammatical_properties(part_of_speech, recipe_output):
    """Create appropriate grammatical properties based on part of speech."""
    if (part_of_speech == "noun"):
        return {
            "$type": "NounProperties",
            "gender": "neutral",  # Default value
            "countability": "countable",  # Default value
            "declension_class": "regular",  # Default value
            "case_forms": {
                "nominative": {
                    "singular": recipe_output.get("Apply_Phonology", {}).get_data().get("updated_word", ""),
                    "plural": ""  # To be filled later
                }
            }
        }
    elif (part_of_speech == "verb"):
        return {
            "$type": "VerbProperties",
            "transitivity": "intransitive",  # Default value
            "conjugation_class": "regular",  # Default value
            "tense_forms": {
                "present": {
                    "first_singular": recipe_output.get("Apply_Phonology", {}).get_data().get("updated_word", ""),
                    "second_singular": "",
                    "third_singular": "",
                    "first_plural": "",
                    "second_plural": "",
                    "third_plural": ""
                }
            },
            "infinitive": ""  # To be filled later
        }
    elif (part_of_speech == "adjective"):
        return {
            "$type": "AdjectiveProperties",
            "comparison": {
                "comparative": "",
                "superlative": ""
            },
            "agreement_forms": {
                "masculine": "",
                "feminine": "",
                "neuter": recipe_output.get("Apply_Phonology", {}).get_data().get("updated_word", ""),
                "plural": ""
            }
        }
    else:
        return {
            "$type": "OtherProperties",
            "variations": {}
        }

    
def apply_phonology_rules(word_base, rules):
    """Apply phonological rules to create a word."""
    # Existing implementation from test_langchain.py

def generate_pronunciation(word, language_profile):
    """Generate pronunciation for a word."""
    # Existing implementation from test_langchain.py

def process_recipe_output(recipe_output):
    """Process recipe output into a word entry."""
    from .models import WordEntryModel
    return WordEntryModel.from_recipe_output(recipe_output)