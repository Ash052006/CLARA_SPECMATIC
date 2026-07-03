"""Shared pytest fixtures for Clara API smoke tests.

Contract compliance is handled by Specmatic. These tests only check lightweight
application behavior that is awkward to express as provider contract scenarios.
"""

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CLARA_CONTRACT_TEST_MODE", "1")

import main as clara_main


@pytest.fixture
def client():
    return TestClient(clara_main.app, raise_server_exceptions=False)


@pytest.fixture
def sample_messages():
    return {
        "normal": "What time is my next meeting?",
        "long": "Please summarize my schedule " * 40,
        "special": "Can you search email from alex@example.com about Q2?",
        "blank": "   ",
    }
