import uuid
from datetime import time

from src.infrastructure.repositories.subject_repository import SubjectRepository


def test_get_conflicting_calls_normalize_and_queries(monkeypatch):
    repo = SubjectRepository(None)

    called = {}
    def fake_norm(days):
        called['days'] = days
        return ['Lunes']

    monkeypatch.setattr(repo, '_normalize_days', fake_norm)

    class DummyQuery:
        def __init__(self):
            self.filter_args = None
        def filter(self, *args):
            self.filter_args = args
            return self
        def all(self):
            return []

    class DummySession:
        def query(self, model):
            return DummyQuery()

    repo.db = DummySession()

    res = repo.get_conflicting(uuid.uuid4(), ['LUNES'], time(9, 0))
    assert called['days'] == ['LUNES']
    assert res == []


def test_create_uses_normalize_and_adds_subject(monkeypatch):
    repo = SubjectRepository(None)

    def fake_norm(days):
        return ['Martes']

    monkeypatch.setattr(repo, '_normalize_days', fake_norm)

    created = {}
    class DummyQuery:
        def __init__(self):
            self.filter_args = None
        def filter(self, *args):
            self.filter_args = args
            return self
        def all(self):
            return []

    class DummySession:
        def __init__(self):
            self.added = None
            self.committed = False
        def query(self, model):
            return DummyQuery()
        def add(self, obj):
            self.added = obj
        def commit(self):
            self.committed = True
        def refresh(self, obj):
            # pretend DB assigned an id
            obj.id = uuid.uuid4()

    repo.db = DummySession()

    subj = repo.create(
        student_id=uuid.uuid4(),
        name='X',
        days=['MARTES'],
        time=time(8, 0),
        teacher='T',
        color='#ffffff',
        type=None,
        replace=False
    )

    # Ensure our fake normalized days was used on the Subject instance
    assert repo.db.added is not None
    assert hasattr(repo.db.added, 'days')
    assert repo.db.added.days == ['Martes']
    assert repo.db.committed is True
    assert subj is not None
