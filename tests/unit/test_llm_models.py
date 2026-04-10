"""Tests for core.domains.llm.models module."""
import pytest
from core.domains.llm.models import LLMRequest, LLMMessage


class TestLLMRequestAddMessage:
    """Tests for LLMRequest.add_message behaviour."""

    def test_add_message_initialises_list_when_messages_is_none(self):
        """add_message must initialise messages list when field is None."""
        req = LLMRequest(model='gpt-4')
        assert req.messages is None
        req.add_message('user', 'hello')
        assert len(req.messages) == 1
        assert req.messages[0].role == 'user'

    def test_add_message_appends_when_list_already_exists(self):
        """add_message must append to an existing list without reinitialising it."""
        req = LLMRequest(model='gpt-4', messages=[LLMMessage(role='system', content='You are helpful.')])
        req.add_message('user', 'hello')
        assert len(req.messages) == 2
        assert req.messages[1].content == 'hello'

    def test_add_message_sets_role_and_content_correctly(self):
        """add_message must create a message with the provided role and content."""
        req = LLMRequest(model='gpt-4')
        req.add_message('assistant', 'I can help with that.')
        assert req.messages[0].role == 'assistant'
        assert req.messages[0].content == 'I can help with that.'
