"""Build data/knowledge.db (Ask Jon's index of Jon's documents) from sources/. Run before packaging:
    python scripts/build_knowledge.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from studio import knowledge  # noqa: E402

if __name__ == "__main__":
    print(knowledge.build(ROOT / "data" / knowledge.DB_NAME, ROOT / "sources"))
