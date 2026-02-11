"""
Rate limiting configuration using slowapi.

Modulo separado para evitar imports circulares entre main.py y auth.py.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
