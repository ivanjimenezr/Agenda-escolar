"""Ensure SQLAlchemy mappers initialize without errors (prevents InvalidRequestError).
"""
import sys

# Ensure backend package is importable when tests are run from project root
sys.path.append("backend")

import pytest
from sqlalchemy.orm import configure_mappers


def test_configure_mappers_no_errors():
    # Import models and run configure_mappers to detect mapping issues early
    import src.domain.models as models  # noqa: F401
    # will raise if mappers cannot initialize
    configure_mappers()
    assert True
