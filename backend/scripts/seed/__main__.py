"""Entry point: python -m scripts.seed"""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.seed.orchestrate import run  # noqa: E402


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
