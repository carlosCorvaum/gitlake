import base64

import pandas as pd
import pytest

from gitlake import connection as connection_module
from gitlake.connection import (
    GitConnection,
    GitHubAPIError,
    GitHubAuthError,
    GitHubConflictError,
    GitHubRateLimitError,
)


class FakeResponse:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


@pytest.fixture
def conn():
    return GitConnection(
        repo_url="https://github.com/owner/repo.git",
        username="user",
        token="secret-token-123",
    )


def test_repr_masks_token(conn):
    assert "secret-token-123" not in repr(conn)
    assert "***" in repr(conn)


def test_auth_url_is_not_stored_as_persistent_attribute(conn):
    assert not hasattr(conn, "auth_url")
    assert "secret-token-123" in conn.get_auth_clone_url()


def test_write_returns_true_on_success(conn, monkeypatch):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(404))
    monkeypatch.setattr(connection_module.requests, "put", lambda *a, **k: FakeResponse(201))
    df = pd.DataFrame({"a": [1, 2]})
    result = conn.write_pd_dataframe_github(
        base_path="data", path="foo", df=df, format="csv", mode="overwrite", message="msg"
    )
    assert result is True


def test_write_returns_false_on_generic_failure(conn, monkeypatch):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(404))
    monkeypatch.setattr(
        connection_module.requests, "put", lambda *a, **k: FakeResponse(422, {"message": "bad request"})
    )
    df = pd.DataFrame({"a": [1]})
    result = conn.write_pd_dataframe_github(
        base_path="data", path="foo", df=df, format="csv", mode="overwrite", message="msg"
    )
    assert result is False


def test_write_raises_conflict_on_409(conn, monkeypatch):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(200, {"sha": "abc"}))
    monkeypatch.setattr(connection_module.requests, "put", lambda *a, **k: FakeResponse(409))
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(GitHubConflictError):
        conn.write_pd_dataframe_github(
            base_path="data", path="foo", df=df, format="csv", mode="overwrite", message="msg"
        )


@pytest.mark.parametrize(
    "status_code, expected_exc",
    [
        (404, FileNotFoundError),
        (401, GitHubAuthError),
        (403, GitHubRateLimitError),
        (429, GitHubRateLimitError),
        (500, GitHubAPIError),
    ],
)
def test_download_status_maps_to_specific_exception(conn, monkeypatch, status_code, expected_exc):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(status_code))
    with pytest.raises(expected_exc):
        conn.read_pd_dataframe_github(base_path="data", path="foo", format="csv")


def test_download_large_file_without_inline_content_raises(conn, monkeypatch):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(200, {}))
    with pytest.raises(GitHubAPIError):
        conn.read_pd_dataframe_github(base_path="data", path="foo", format="csv")


def test_download_success_roundtrip(conn, monkeypatch):
    df = pd.DataFrame({"a": [1, 2]})
    content_b64 = base64.b64encode(df.to_csv(index=False).encode()).decode()
    monkeypatch.setattr(
        connection_module.requests, "get", lambda *a, **k: FakeResponse(200, {"content": content_b64})
    )
    result = conn.read_pd_dataframe_github(base_path="data", path="foo", format="csv")
    assert list(result["a"]) == [1, 2]


def test_delete_from_github_success(conn, monkeypatch):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(200, {"sha": "abc"}))
    monkeypatch.setattr(connection_module.requests, "delete", lambda *a, **k: FakeResponse(200))
    assert conn.delete_from_github(base_path="data", path="foo", format="csv", message="bye") is True


def test_delete_from_github_missing_file_raises(conn, monkeypatch):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(404))
    with pytest.raises(FileNotFoundError):
        conn.delete_from_github(base_path="data", path="foo", format="csv", message="bye")


def test_delete_from_github_conflict_raises(conn, monkeypatch):
    monkeypatch.setattr(connection_module.requests, "get", lambda *a, **k: FakeResponse(200, {"sha": "abc"}))
    monkeypatch.setattr(connection_module.requests, "delete", lambda *a, **k: FakeResponse(409))
    with pytest.raises(GitHubConflictError):
        conn.delete_from_github(base_path="data", path="foo", format="csv", message="bye")
