"""
Architecture test specific fixtures and configuration.
"""
import pytest

# Architecture test specific fixtures can go here
@pytest.fixture
def domain_registration_fixture():
    """Example fixture for domain registration tests."""
    # Setup code
    yield
    # Teardown code