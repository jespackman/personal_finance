#Point the app at a throwaway data file and never open a browser while testing.
#These must be set before storage.py is imported, so they live at the top of conftest.
import os
import tempfile

TEST_DATA_FILE = os.path.join(tempfile.mkdtemp(), "accounts.json")
os.environ["FINANCE_APP_DATA_FILE"] = TEST_DATA_FILE
os.environ["FINANCE_APP_NO_BROWSER"] = "1"
os.environ["FINANCE_APP_SECRET"] = "test-secret"

import pytest

pytest_plugins = ["nicegui.testing.user_plugin"]


#Start every test with no accounts
@pytest.fixture(autouse=True)
def fresh_data():
    if os.path.exists(TEST_DATA_FILE):
        os.remove(TEST_DATA_FILE)
    yield
