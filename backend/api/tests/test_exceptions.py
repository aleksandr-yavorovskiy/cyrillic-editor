import pytest
from api.core.exceptions import APIError


class TestAPIError:
    def test_basic_exception(self):
        error = APIError("Test error")
        assert str(error) == "Test error"
        assert error.status_code == 500
