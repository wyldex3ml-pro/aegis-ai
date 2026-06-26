import os
import uuid
import logging
from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aegis.rag")

COLLECTION_NAME = "aegis_incidents"
VECTOR_SIZE = 384


def embed_text(text: str) -> list[float]:
    import hashlib
    hash_bytes = hashlib.sha256(text.encode("utf-8")).digest()
    vector = []
    for i in range(VECTOR_SIZE):
        byte_val = hash_bytes[i % len(hash_bytes)]
        varied = (byte_val ^ (i * 7)) % 256
        vector.append((varied / 127.5) - 1.0)
    return vector


class RagStorage:
    def __init__(self):
        logger.info("Initialising Qdrant in-memory client...")
        self.client = QdrantClient(":memory:")
        self._initialise_collection()
        logger.info("✅ RagStorage ready.")

    def _initialise_collection(self):
        existing = self.client.get_collections().collections
        existing_names = [c.name for c in existing]
        if COLLECTION_NAME not in existing_names:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            logger.info("Created collection: '%s'", COLLECTION_NAME)

    def store_incident(self, error_log: str, patch: str, outcome: str,
                       repo_url: Optional[str] = None, retry_count: int = 0) -> str:
        incident_id = str(uuid.uuid4())
        vector = embed_text(error_log)
        payload = {
            "error_log": error_log,
            "patch": patch,
            "outcome": outcome,
            "repo_url": repo_url or "unknown",
            "retry_count": retry_count,
        }
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(id=incident_id, vector=vector, payload=payload)],
        )
        logger.info("Stored incident [%s...] | outcome=%s", incident_id[:8], outcome)
        return incident_id

    def retrieve_similar(self, error_log: str, top_k: int = 3) -> str:
        info = self.client.get_collection(COLLECTION_NAME)
        if info.points_count == 0:
            return "No historical incidents found."
        query_vector = embed_text(error_log)
        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
        )
        results = response.points
        if not results:
            return "No similar past incidents found."
        logger.info("Retrieved %d similar incident(s).", len(results))
        context_parts = []
        for i, hit in enumerate(results, start=1):
            p = hit.payload
            context_parts.append(
                f"--- PAST INCIDENT #{i} (similarity: {int(hit.score * 100)}%) ---\n"
                f"Error      : {p.get('error_log', '')}\n"
                f"Fix Applied: {p.get('patch', '')}\n"
                f"Outcome    : {p.get('outcome', '')} ({p.get('retry_count', 0)} retries)\n"
            )
        return "\n".join(context_parts)

    def get_stats(self) -> dict:
        info = self.client.get_collection(COLLECTION_NAME)
        return {"total_incidents": info.points_count, "collection_name": COLLECTION_NAME}

    def seed_with_examples(self):
        logger.info("Seeding RAG database...")
        examples = [
            {
                "error_log": "AttributeError: 'NoneType' object has no attribute 'total'\n  File 'payment/processor.py', line 42",
                "patch": "def process_payment(cart):\n    if cart is None:\n        raise ValueError('Cart cannot be None')\n    return cart.total()",
                "outcome": "fixed",
                "repo_url": "https://github.com/demo-org/payment-service",
                "retry_count": 1,
            },
            {
                "error_log": "KeyError: 'user_id'\n  File 'api/auth.py', line 88, in validate_token",
                "patch": "def validate_token(request):\n    user_id = request.session.get('user_id')\n    if user_id is None:\n        return None\n    return user_id",
                "outcome": "fixed",
                "repo_url": "https://github.com/demo-org/auth-service",
                "retry_count": 0,
            },
            {
                "error_log": "RecursionError: maximum recursion depth exceeded\n  File 'utils/tree.py', line 23",
                "patch": "def flatten_tree(node, depth=0, max_depth=100):\n    if depth > max_depth:\n        raise ValueError('Max depth exceeded')\n    result = [node.value]\n    for child in node.children:\n        result.extend(flatten_tree(child, depth+1, max_depth))\n    return result",
                "outcome": "fixed",
                "repo_url": "https://github.com/demo-org/data-pipeline",
                "retry_count": 1,
            },
        ]
        for ex in examples:
            self.store_incident(**ex)
        logger.info("✅ Seeded %d examples.", len(examples))


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  AegisAI — Phase 2 RAG Validation")
    print("=" * 50)

    rag = RagStorage()
    rag.seed_with_examples()

    stats = rag.get_stats()
    print(f"\n✅ Database stats: {stats}")

    result = rag.retrieve_similar(
        "AttributeError: 'NoneType' object has no attribute 'price'\n  File 'store/checkout.py', line 31"
    )
    print(f"\n✅ Retrieval result:\n{result}")
    print("✅ Phase 2 complete.\n")