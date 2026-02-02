import pytest

from src.infrastructure.repositories.subject_repository import SubjectRepository


def test_normalize_days_uppercase_and_mixed():
    repo = SubjectRepository(None)
    input_days = ["LUNES", "MARTES", "MIERCOLES"]
    result = repo._normalize_days(input_days)
    assert result == ["Lunes", "Martes", "Miércoles"]


def test_normalize_days_various_cases_and_accents():
    repo = SubjectRepository(None)
    input_days = ["lunes", "Miércoles", "Sábado"]
    result = repo._normalize_days(input_days)
    assert result == ["Lunes", "Miércoles", "Sábado"]


def test_normalize_ignores_invalid_entries():
    repo = SubjectRepository(None)
    input_days = ["LUNES", "NOTADAY", 123, None]
    result = repo._normalize_days(input_days)
    assert result == ["Lunes"]
