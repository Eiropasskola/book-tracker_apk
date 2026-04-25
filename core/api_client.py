"""Open Library API klients."""
import os
import requests
from typing import List, Optional
from urllib.parse import quote


SEARCH_URL = "https://openlibrary.org/search.json"
COVER_URL = "https://covers.openlibrary.org/b/{key}/{value}-{size}.jpg"


class OpenLibraryClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def search(self, query: str, limit: int = 20) -> List[dict]:
        """Meklē grāmatas. Atgriež sarakstu ar dict objektiem."""
        if not query.strip():
            return []
        try:
            response = requests.get(
                SEARCH_URL,
                params={'q': query, 'limit': limit},
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"[API kļūda] {e}")
            return []

        results = []
        for doc in data.get('docs', []):
            isbn_list = doc.get('isbn', [])
            isbn = isbn_list[0] if isbn_list else ''
            results.append({
                'title': doc.get('title', ''),
                'author': ', '.join(doc.get('author_name', [])),
                'isbn': isbn,
                'pages': doc.get('number_of_pages_median', 0) or 0,
                'first_publish_year': doc.get('first_publish_year', ''),
                'cover_id': doc.get('cover_i'),
                'subject': doc.get('subject', [])[:3] if doc.get('subject') else [],
            })
        return results

    def download_cover(self, isbn: str = '', cover_id: Optional[int] = None,
                       save_dir: str = 'assets/covers',
                       size: str = 'M') -> Optional[str]:
        """Lejupielādē vāku. Atgriež saglabātā faila ceļu vai None."""
        os.makedirs(save_dir, exist_ok=True)

        if cover_id:
            url = COVER_URL.format(key='id', value=cover_id, size=size)
            filename = f"cover_{cover_id}.jpg"
        elif isbn:
            url = COVER_URL.format(key='isbn', value=quote(isbn), size=size)
            filename = f"isbn_{isbn}.jpg"
        else:
            return None

        save_path = os.path.join(save_dir, filename)
        if os.path.exists(save_path) and os.path.getsize(save_path) > 100:
            return save_path

        try:
            response = requests.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            content = response.content
            # Open Library atgriež 1px placeholder, ja vāka nav (~800 baiti)
            if len(content) < 1000:
                return None
            with open(save_path, 'wb') as f:
                f.write(content)
            return save_path
        except requests.RequestException as e:
            print(f"[Vāka lejupielādes kļūda] {e}")
            return None
