import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


@pytest.fixture(scope="session")
def fixture_sessions_path():
    from tests.fixtures.generate_fixture import write_fixture
    return write_fixture()
