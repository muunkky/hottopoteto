"""
Generic storage module for persisting and retrieving recipe outputs.
"""
from .repository import Repository
from .indexing import update_indices, search_by_criteria, load_index
