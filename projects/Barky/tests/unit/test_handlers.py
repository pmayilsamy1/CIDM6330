from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List

import pytest
from barkylib import bootstrap
from barkylib.adapters import repository
from barkylib.domain import commands
from barkylib.services import handlers, unit_of_work


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next(
            (p for p in self._products for b in p.batches if b.reference == batchref),
            None,
        )

class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.services = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass

class FakeNotifications(notifications.AbstractNotifications):
    def __init__(self):
        self.sent = defaultdict(list)  # type: Dict[str, List[str]]

    def send(self, destination, message):
        self.sent[destination].append(message)

def bootstrap_test_app():
    return bootstrap.bootstrap(
        start_orm=False,
        uow=FakeUnitOfWork(),
        notifications=FakeNotifications(),
        publish=lambda *args: None,
    )

class TestAddBookmark:
    def test_add_bookmark(self):
        bus = bootstrap_test_app()
        created = datetime.now().isoformat()
        edited = created
        bus.handle(commands.AddBookmarkCommand(0, "test", "http://www.example/com", None, created, edited))
        assert bus.uow.services.get("HairCut") is not None
        assert bus.uow.committed

def test_for_existing_bookmark(self):
        bus = bootstrap_test_app()
        created = datetime.now().isoformat()
        edited = created
        bus.handle(commands.AddBookmarkCommand(0, "test", "http://www.example/com", None, created, edited)))
        bus.handle(commands.AddBookmarkCommand(0, "test", "http://www.example/com", None, created, edited)))
        assert "test" in [
            b.service_name for b in bus.uow.services.get("test").bookmarks
        ]

