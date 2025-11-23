"""
Pytest configuration and shared fixtures for manufacturing tests
"""
import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Add pytest-asyncio to requirements:
# pytest-asyncio==0.21.1
# pytest==7.4.0
