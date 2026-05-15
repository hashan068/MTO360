"""Shared session + Faker instance for the seed orchestrator."""
import random

from faker import Faker

from app.config.database import AsyncSessionLocal

SEED = 42

fake = Faker()
Faker.seed(SEED)
random.seed(SEED)


__all__ = ["AsyncSessionLocal", "fake", "random", "SEED"]
