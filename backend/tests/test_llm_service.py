import pytest
from app.services.llm_service import build_final_prompt


def test_build_final_prompt_basic():
    template = "Hello {{name}}, today is {{day}}"
    variables = {"name": "Alice", "day": "Monday"}
    result = build_final_prompt(template, variables)
    assert result == "Hello Alice, today is Monday"


def test_build_final_prompt_missing_var():
    template = "Hello {{name}}, you are {{age}}"
    variables = {"name": "Bob"}
    result = build_final_prompt(template, variables)
    assert result == "Hello Bob, you are {{age}}"


def test_build_final_prompt_no_variables():
    template = "Hello World"
    variables = {}
    result = build_final_prompt(template, variables)
    assert result == "Hello World"


def test_build_final_prompt_partial_replace():
    template = "{{a}}{{b}}{{c}}"
    variables = {"a": "1", "c": "3"}
    result = build_final_prompt(template, variables)
    assert result == "1{{b}}3"
