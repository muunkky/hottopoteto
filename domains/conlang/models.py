from core.models import GenericEntryModel

class WordEntryModel(GenericEntryModel):
    """Conlang-specific word model."""
    eldorian: str
    english: str
    # All other conlang-specific fields