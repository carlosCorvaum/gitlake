import dataclasses
from unittest.mock import MagicMock

import pandas as pd
import pytest

from gitlake.collections import Collection, CollectionManager
from gitlake.connection import GitConnection


def _metadata_df(collections):
    return pd.DataFrame([dataclasses.asdict(c) for c in collections])


@pytest.fixture
def empty_git_connection():
    conn = MagicMock(spec=GitConnection)
    conn.read_pd_dataframe_github.side_effect = FileNotFoundError("no metadata yet")
    return conn


@pytest.fixture
def manager(empty_git_connection):
    return CollectionManager(git_connection=empty_git_connection)


def existing_collection_manager(
    collection, metadata_base_path="metadata", metadata_path="collections_registry"
):
    conn = MagicMock(spec=GitConnection)

    def fake_read(base_path, path, format):
        if base_path == metadata_base_path and path == metadata_path:
            return _metadata_df([collection])
        raise FileNotFoundError(f"no file at {base_path}/{path}")

    conn.read_pd_dataframe_github.side_effect = fake_read
    manager = CollectionManager(git_connection=conn)
    return manager, conn


def test_collection_created_at_uses_default_factory_not_a_fixed_value():
    # A plain `= datetime.now().isoformat()` default is evaluated once at class
    # definition time; every Collection would share the same timestamp. A
    # default_factory is re-evaluated per instance.
    created_at_field = next(f for f in dataclasses.fields(Collection) if f.name == "created_at")
    assert created_at_field.default_factory is not dataclasses.MISSING


def test_create_collection_rejects_unsupported_format(manager):
    bad = Collection(name="x", base_path="data", path="x", format="xml")
    with pytest.raises(ValueError):
        manager.create_collection(bad)


def test_save_dataframe_rejects_unsupported_mode(manager):
    with pytest.raises(ValueError):
        manager.save_dataframe(pd.DataFrame(), "x", mode="invalid-mode")


def test_delete_collection_passes_format_to_delete_from_github():
    coll = Collection(name="x", base_path="data", path="x", format="parquet")
    manager, conn = existing_collection_manager(coll)
    conn.write_pd_dataframe_github.return_value = True
    conn.delete_from_github.return_value = True

    assert manager.delete_collection("x") is True

    _, kwargs = conn.delete_from_github.call_args
    assert kwargs["format"] == "parquet"


def test_delete_collection_missing_method_no_longer_breaks():
    # Regression test for the AttributeError bug: GitConnection used to have no
    # delete_from_github method at all, so this call would always crash.
    coll = Collection(name="x", base_path="data", path="x", format="csv")
    manager, conn = existing_collection_manager(coll)
    conn.write_pd_dataframe_github.return_value = True
    conn.delete_from_github.return_value = True

    manager.delete_collection("x")  # must not raise AttributeError

    conn.delete_from_github.assert_called_once()


def test_save_dataframe_propagates_write_failure():
    coll = Collection(name="x", base_path="data", path="x", format="csv")
    manager, conn = existing_collection_manager(coll)

    def write_side_effect(base_path, path, df, format, mode, message):
        return not (base_path == "data" and path == "x")  # metadata write ok, data write fails

    conn.write_pd_dataframe_github.side_effect = write_side_effect

    assert manager.save_dataframe(pd.DataFrame({"a": [1]}), "x") is False


def test_save_dataframe_returns_true_on_success():
    coll = Collection(name="x", base_path="data", path="x", format="csv")
    manager, conn = existing_collection_manager(coll)
    conn.write_pd_dataframe_github.return_value = True

    assert manager.save_dataframe(pd.DataFrame({"a": [1]}), "x") is True


def test_read_dataframe_returns_none_when_collection_data_missing():
    coll = Collection(name="x", base_path="data", path="x", format="csv")
    manager, conn = existing_collection_manager(coll)

    assert manager.read_dataframe("x") is None
