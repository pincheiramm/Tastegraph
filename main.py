import sys
import urllib.request
from urllib.parse import quote_plus

import albumoftheyearapi.artist as _artist_mod
from albumoftheyearapi import AOTY
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class _PatchedRequest(urllib.request.Request):
    def __init__(self, url, data=None, headers={}, **kwargs):
        headers = {**headers, "User-Agent": UA}
        super().__init__(url, data, headers, **kwargs)


_artist_mod.Request = _PatchedRequest


def search_artist(name: str) -> list[tuple[str, str]]:
    """Returns [(slug, display_name), ...] for the given artist name."""
    url = f"https://www.albumoftheyear.org/search/artists/?q={quote_plus(name)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req).read()
    soup = BeautifulSoup(html, "html.parser")

    seen = set()
    results = []
    for a in soup.select("a[href*='/artist/']"):
        href = a["href"]          # e.g. /artist/183-kanye-west/
        slug = str(href).strip("/").split("/")[-1]   # 183-kanye-west
        label = a.text.strip()
        if slug and label and slug not in seen:
            seen.add(slug)
            results.append((slug, label))
    return results


def show_discography(artist_slug: str) -> None:
    client = AOTY()
    print(f"\n=== Discografía de {client.artist_name(artist_slug)} ===\n")
    sections = [
        ("Álbumes",  client.artist_albums),
        ("Mixtapes", client.artist_mixtapes),
        ("EPs",      client.artist_eps),
        ("Singles",  client.artist_singles),
    ]
    for label, method in sections:
        items = method(artist_slug)
        if items:
            print(f"--- {label} ---")
            for item in items:
                print(f"  {item}")
            print()


def main() -> None:
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Artista: ")

    results = search_artist(query)
    if not results:
        print("No se encontraron artistas.")
        return

    if len(results) == 1:
        show_discography(results[0][0])
        return

    print(f"\nResultados para '{query}':")
    for i, (slug, name) in enumerate(results[:8], 1):
        print(f"  {i}. {name}  ({slug})")

    choice = input("\nElige un número: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(results[:8]):
        show_discography(results[int(choice) - 1][0])


main()
