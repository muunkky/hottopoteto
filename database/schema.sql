CREATE TABLE Lexicon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Basic information
    canonical_form TEXT NOT NULL,          -- The definitive form of the word
    language TEXT NOT NULL,                -- E.g. "English", "Spanish", ISO code, etc.
    part_of_speech TEXT NOT NULL,          -- Verb, Noun, Adjective, etc.
    connotation TEXT,                      -- Extra nuance or implied meaning
    declension TEXT,                       -- Declension classification (or "N/A")
    
    -- Morphological details
    base_word TEXT,                        -- The single base word (if applicable)
    compound_base_word TEXT,               -- For compound words as generated from base words
    inflected_forms TEXT,                  -- Comma-separated list (or JSON) of inflected forms
    
    -- Verb-specific properties
    verb_regularity TEXT,                  -- "Regular", "Irregular", etc.
    tense_forms TEXT,                      -- Structured string (or JSON) for Present, Past, Gerund, etc.
    
    -- Noun, Adjective properties
    noun_type TEXT,                        -- E.g. "Gerund", "Collective", etc.
    adjective_type TEXT,                   -- E.g. "Descriptive", "Reflexive", etc.
    
    -- Other parts of speech
    adverb_type TEXT,                      -- E.g. "Manner", "Frequency", etc.
    preposition_type TEXT,                 -- E.g. "Spatial", "Temporal", "Metaphorical", etc.
    conjunction_type TEXT,                 -- E.g. "Coordinating", "Subordinating"
    
    -- Usage, semantic and syntactic info
    common_usage TEXT,                     -- Sample usage sentence(s) or notes
    function TEXT,                         -- Describes the syntactic/functional role in sentences
    synonyms TEXT,                         -- Comma-separated or JSON list
    antonyms TEXT,                         -- Comma-separated or JSON list
    additional_features TEXT,              -- Any extra flags or notes (e.g. "can also be X")
    position_in_sentence TEXT,             -- Typical positional information
    common_collocations TEXT,              -- Collocations or common phrases
    multi_word_forms TEXT,                 -- Multi-word or idiomatic expressions
    idiomatic_usage TEXT,                  -- Notes on idiomatic or figurative operations
    
    -- Phonetic and etymological data
    etymology TEXT,                        -- Historical origins and derivations
    ipa_pronunciation TEXT,                -- IPA transcription
    phonetic_syllables TEXT,               -- Syllable breakdown
    common_mistakes TEXT,                  -- Common errors/traps in usage
    
    -- Morphology & final processing
    morphology TEXT,                       -- Summary of morphology adjustments applied
    updated_word TEXT,                     -- The final form after all processing
    revised_connotation TEXT,              -- Revised or expanded connotation, if applicable
    
    -- Extra miscellaneous data (if needed)
    extra_info TEXT,                       -- JSON or free text for additional metadata
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Useful indexes for fast lookups:
CREATE INDEX idx_lexicon_canonical_form ON Lexicon(canonical_form);
CREATE INDEX idx_lexicon_language ON Lexicon(language);
CREATE INDEX idx_lexicon_part_of_speech ON Lexicon(part_of_speech);
CREATE INDEX idx_lexicon_created_at ON Lexicon(created_at);