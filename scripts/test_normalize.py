import sys
# Add backend/src to PYTHONPATH so we can import the project packages
sys.path.insert(0, "backend/src")
# Import the repository directly from file to avoid importing package-level dependencies
# We'll run a local copy of the normalization logic to verify behavior without importing SQLAlchemy
import unicodedata
import enum

class Weekday(enum.Enum):
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


def _normalize_days(days):
    def strip_accents(s: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    WeekdayEnum = Weekday
    normalized_days = []
    for d in days:
        val = None
        if isinstance(d, WeekdayEnum):
            val = d.value
        elif isinstance(d, str):
            s = d.strip()
            for member in WeekdayEnum:
                if s.lower() == member.value.lower():
                    val = member.value
                    break
            if val is None:
                member = WeekdayEnum.__members__.get(s.upper())
                if member is not None:
                    val = member.value
            if val is None:
                s_norm = strip_accents(s.lower())
                for member in WeekdayEnum:
                    if strip_accents(member.value.lower()) == s_norm:
                        val = member.value
                        break
        if val is not None:
            normalized_days.append(val)
    return normalized_days

repo_normalize = _normalize_days

tests = [
    ["LUNES", "MARTES", "MIERCOLES"],
    ["lunes", "Miércoles", "Sábado"],
    ["LUNES", "miercoles", "Miercoles"],
    ["LUNES", "MIERCOLES", "MIERCOLES"],
    ["LUNES", "Martes", "DOMINGO"],
]

for t in tests:
    print(t, "->", repo_normalize(t))
