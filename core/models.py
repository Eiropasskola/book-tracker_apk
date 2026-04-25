"""Datu klases grāmatu izsekotājam."""
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional


STATUS_CHOICES = ['want_to_read', 'reading', 'finished', 'abandoned']
STATUS_LABELS = {
    'want_to_read': 'Vēlos lasīt',
    'reading': 'Lasu',
    'finished': 'Izlasīta',
    'abandoned': 'Pamesta',
}


@dataclass
class Book:
    id: Optional[int] = None
    title: str = ''
    author: str = ''
    isbn: str = ''
    pages: int = 0
    genre: str = ''
    status: str = 'want_to_read'
    rating: int = 0  # 0 = nav vērtējuma, 1-5 = zvaigznes
    notes: str = ''
    cover_path: str = ''
    started_date: Optional[str] = None  # ISO format YYYY-MM-DD
    finished_date: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def status_label(self) -> str:
        return STATUS_LABELS.get(self.status, self.status)


@dataclass
class Goal:
    id: Optional[int] = None
    year: int = 0
    target_books: int = 0
    target_pages: int = 0

    def to_dict(self) -> dict:
        return asdict(self)
