"""CSV un JSON eksports."""
import csv
import json
from typing import List
from core.models import Book, Goal


def export_csv(books: List[Book], filepath: str) -> None:
    fieldnames = ['id', 'title', 'author', 'isbn', 'pages', 'genre',
                  'status', 'rating', 'notes', 'started_date',
                  'finished_date', 'created_at']
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for book in books:
            row = book.to_dict()
            row.pop('cover_path', None)
            writer.writerow(row)


def export_json(books: List[Book], goals: List[Goal], filepath: str) -> None:
    data = {
        'version': '1.0',
        'books': [b.to_dict() for b in books],
        'goals': [g.to_dict() for g in goals],
    }
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
