from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.qparser import QueryParser
import os

def create_index(pages_data):
    schema = Schema(url=TEXT(stored=True), content=TEXT)
    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema)
    writer = ix.writer()

    for url, content in pages_data.items():
        writer.add_document(url=url, content=content)

    writer.commit()

def search_query(query):
    from whoosh.index import open_dir
    ix = open_dir("index")
    with ix.searcher() as searcher:
        query_parser = QueryParser("content", ix.schema)
        query = query_parser.parse(query)
        results = searcher.search(query)
        return results