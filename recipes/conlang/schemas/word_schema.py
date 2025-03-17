WORD_SCHEMA = {
    "type": "object",
    "required": ["eldorian", "english", "part_of_speech"],
    "properties": {
        "eldorian": {"type": "string"},
        "english": {"type": "string"},
        "part_of_speech": {
            "type": "string",
            "enum": ["noun", "verb", "adjective", "adverb", "pronoun", "preposition"]
        },
        "grammatical_properties": {"type": "object"}
    }
}
