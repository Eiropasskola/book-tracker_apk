"""SQLite datubāzes pārvaldība."""
import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from core.models import Book, Goal


class Database:
    def __init__(self, db_path: str = 'books.db'):
        self.db_path = db_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT DEFAULT '',
                    isbn TEXT DEFAULT '',
                    pages INTEGER DEFAULT 0,
                    genre TEXT DEFAULT '',
                    status TEXT DEFAULT 'want_to_read'
                        CHECK(status IN ('want_to_read','reading','finished','abandoned')),
                    rating INTEGER DEFAULT 0 CHECK(rating BETWEEN 0 AND 5),
                    notes TEXT DEFAULT '',
                    cover_path TEXT DEFAULT '',
                    started_date TEXT,
                    finished_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER UNIQUE NOT NULL,
                    target_books INTEGER NOT NULL DEFAULT 0,
                    target_pages INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
                CREATE INDEX IF NOT EXISTS idx_books_finished ON books(finished_date);
            """)

    # ---------- BOOKS ----------
    def add_book(self, book: Book) -> int:
        with self._connect() as conn:
            cursor = conn.execute("""
                INSERT INTO books (title, author, isbn, pages, genre, status,
                                   rating, notes, cover_path, started_date, finished_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (book.title, book.author, book.isbn, book.pages, book.genre,
                  book.status, book.rating, book.notes, book.cover_path,
                  book.started_date, book.finished_date))
            return cursor.lastrowid

    def update_book(self, book: Book) -> None:
        with self._connect() as conn:
            conn.execute("""
                UPDATE books SET title=?, author=?, isbn=?, pages=?, genre=?,
                                 status=?, rating=?, notes=?, cover_path=?,
                                 started_date=?, finished_date=?
                WHERE id=?
            """, (book.title, book.author, book.isbn, book.pages, book.genre,
                  book.status, book.rating, book.notes, book.cover_path,
                  book.started_date, book.finished_date, book.id))

    def delete_book(self, book_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM books WHERE id=?", (book_id,))

    def get_book(self, book_id: int) -> Optional[Book]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
            return self._row_to_book(row) if row else None

    def list_books(self, status: Optional[str] = None,
                   search: Optional[str] = None,
                   genre: Optional[str] = None,
                   sort_by: str = 'created_at') -> List[Book]:
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        if status:
            query += " AND status=?"
            params.append(status)
        if genre:
            query += " AND genre=?"
            params.append(genre)
        if search:
            query += " AND (title LIKE ? OR author LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like])

        sort_map = {
            'created_at': 'created_at DESC',
            'title': 'title ASC',
            'rating': 'rating DESC',
            'finished_date': 'finished_date DESC',
        }
        query += f" ORDER BY {sort_map.get(sort_by, 'created_at DESC')}"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_book(r) for r in rows]

    def get_all_genres(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT genre FROM books WHERE genre != '' ORDER BY genre"
            ).fetchall()
            return [r['genre'] for r in rows]

    @staticmethod
    def _row_to_book(row) -> Book:
        return Book(
            id=row['id'], title=row['title'], author=row['author'],
            isbn=row['isbn'], pages=row['pages'], genre=row['genre'],
            status=row['status'], rating=row['rating'], notes=row['notes'],
            cover_path=row['cover_path'], started_date=row['started_date'],
            finished_date=row['finished_date'], created_at=row['created_at'],
        )

    # ---------- GOALS ----------
    def set_goal(self, goal: Goal) -> None:
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO goals (year, target_books, target_pages)
                VALUES (?, ?, ?)
                ON CONFLICT(year) DO UPDATE SET
                    target_books = excluded.target_books,
                    target_pages = excluded.target_pages
            """, (goal.year, goal.target_books, goal.target_pages))

    def get_goal(self, year: int) -> Optional[Goal]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM goals WHERE year=?", (year,)).fetchone()
            if row:
                return Goal(id=row['id'], year=row['year'],
                          target_books=row['target_books'],
                          target_pages=row['target_pages'])
            return None

    def list_goals(self) -> List[Goal]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM goals ORDER BY year DESC").fetchall()
            return [Goal(id=r['id'], year=r['year'],
                        target_books=r['target_books'],
                        target_pages=r['target_pages']) for r in rows]

    # ---------- SETTINGS ----------
    def get_setting(self, key: str, default: str = '') -> str:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return row['value'] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as conn:
            conn.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))

    # ---------- STATISTIKAS PALĪGFUNKCIJAS ----------
    def books_finished_by_month(self, year: int) -> dict:
        """Atgriež {1: 3, 2: 5, ...} - cik grāmatas izlasītas katrā mēnesī."""
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT CAST(strftime('%m', finished_date) AS INTEGER) AS month,
                       COUNT(*) AS cnt
                FROM books
                WHERE status='finished' AND finished_date IS NOT NULL
                  AND strftime('%Y', finished_date) = ?
                GROUP BY month
            """, (str(year),)).fetchall()
            result = {m: 0 for m in range(1, 13)}
            for row in rows:
                if row['month']:
                    result[row['month']] = row['cnt']
            return result

    def books_by_genre(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT genre, COUNT(*) AS cnt FROM books
                WHERE status='finished' AND genre != ''
                GROUP BY genre ORDER BY cnt DESC
            """).fetchall()
            return {r['genre']: r['cnt'] for r in rows}

    def avg_rating_by_year(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT strftime('%Y', finished_date) AS year,
                       AVG(rating) AS avg_rating
                FROM books
                WHERE status='finished' AND rating > 0 AND finished_date IS NOT NULL
                GROUP BY year ORDER BY year
            """).fetchall()
            return {r['year']: round(r['avg_rating'], 2) for r in rows}

    def finished_count_for_year(self, year: int) -> int:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS cnt FROM books
                WHERE status='finished' AND strftime('%Y', finished_date)=?
            """, (str(year),)).fetchone()
            return row['cnt'] or 0

    def pages_count_for_year(self, year: int) -> int:
        with self._connect() as conn:
            row = conn.execute("""
                SELECT COALESCE(SUM(pages), 0) AS total FROM books
                WHERE status='finished' AND strftime('%Y', finished_date)=?
            """, (str(year),)).fetchone()
            return row['total'] or 0
