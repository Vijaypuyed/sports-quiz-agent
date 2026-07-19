import os
import json
import chromadb
from chromadb.utils import embedding_functions

# =========================================
# CHROMA DATABASE CLIENT
# =========================================
def get_chroma_client():
    """
    Initialize and return a persistent
    ChromaDB client.
    The database is stored locally on disk
    inside the chroma_db directory.
    """
    return chromadb.PersistentClient(
        path="./chroma_db"
    )
# =========================================
# COLLECTION
# =========================================
def get_sports_collection():
    """
    Get or create the sports history
    ChromaDB collection.
    """
    client = get_chroma_client()
    embedding_fn = (
        embedding_functions
        .DefaultEmbeddingFunction()
    )
    collection = (
        client
        .get_or_create_collection(
            name="sports_history",
            embedding_function=embedding_fn
        )
    )
    return collection
# =========================================
# DATABASE SETUP
# =========================================
def setup_and_populate_db(
    json_file_path="./data/sports_facts.json"
):
    """
    Read sports facts from JSON,
    convert them into embeddings,
    and store them in ChromaDB.
    This function only inserts data if
    the collection is empty.
    """
    collection = (
        get_sports_collection()
    )
    # -------------------------------------
    # Prevent duplicate insertion
    # -------------------------------------
    if collection.count() > 0:
        print(
            "Database already populated "
            f"with {collection.count()} facts."
        )
        return collection
    # -------------------------------------
    # Check JSON file
    # -------------------------------------
    if not os.path.exists(
        json_file_path
    ):
        print(
            "Error: Raw fact data file "
            f"not found at {json_file_path}"
        )
        return collection
    # -------------------------------------
    # Load JSON data
    # -------------------------------------
    with open(
        json_file_path,
        "r",
        encoding="utf-8"
    ) as file:
        facts_list = json.load(
            file
        )
    documents = []
    metadata_list = []
    ids = []
    # -------------------------------------
    # Prepare documents
    # -------------------------------------
    for index, item in enumerate(
        facts_list
    ):
        documents.append(
            item["fact"]
        )
        metadata_list.append(
            {
                "sport": item["sport"]
            }
        )
        ids.append(
            f"fact_{index}"
        )
    # -------------------------------------
    # Store in ChromaDB
    # -------------------------------------
    collection.add(
        documents=documents,
        metadatas=metadata_list,
        ids=ids
    )
    print(
        "Successfully vectorized "
        f"and stored {len(documents)} facts."
    )
    return collection
# =========================================
# BACKWARD-COMPATIBLE LOAD FUNCTION
# =========================================
def load_data():
    """
    Compatibility wrapper used by app.py.
    It initializes and populates ChromaDB.
    """
    return setup_and_populate_db()
# =========================================
# QUERY HISTORICAL FACTS
# =========================================
def query_historic_facts(
    sport,
    query_text,
    n_results=3

):

    """
    Query ChromaDB for historical facts
    related to a specific sport.
    Results are filtered using sport metadata.
    """
    collection = (
        get_sports_collection()
    )
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={
            "sport": sport
        }
    )
    return results.get(
        "documents",
        [[]]
    )[0]


# =========================================
# BACKWARD-COMPATIBLE SEARCH FUNCTION
# =========================================

def search_facts(
    sport,
    query,
    n_results=3
):
    """
    Existing function used by generator.py.
    Internally uses the reusable
    query_historic_facts() function.
    """

    return query_historic_facts(
        sport=sport,
        query_text=query,
        n_results=n_results
    )