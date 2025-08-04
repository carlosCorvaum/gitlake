from dataclasses import dataclass
import datetime
import pandas as pd
from gitlake.connection import GitConnection
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class Collection:
    name: str
    base_path: str
    path: str
    format: str
    created_at: str = datetime.datetime.now().isoformat()
    updated_at: str = None

def refresh_collection_list(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self.collection_list = self._get_collections()
        return method(self, *args, **kwargs)
    return wrapper

class CollectionManager:
    def __init__(
        self,
        git_connection: GitConnection,
        metadata_base_path: str = "metadata",
        metadata_path: str = "collections_registry",
    ):
        self.git_connection = git_connection
        self.metadata_base_path = metadata_base_path
        self.metadata_path = metadata_path
        self.collection_list: list[Collection] = self._get_collections()
        logger.info("CollectionManager initialized.")

    def _get_collections(self) -> list[Collection]:
        try:
            df = self.git_connection.read_pd_dataframe_github(
                base_path=self.metadata_base_path,
                path=self.metadata_path,
                format="json",
            )
            logger.info("📖 Collections metadata loaded successfully.")
            return [Collection(**row) for row in df.to_dict(orient="records")]
        except FileNotFoundError:
            logger.warning("No collections registered yet.")
            return []

    @refresh_collection_list
    def collection_exists(self, name: str) -> bool:
        return any(c.name == name for c in self.collection_list)

    @refresh_collection_list
    def create_collection_folder(self, collection: Collection):
        empty_df = pd.DataFrame()
        self.git_connection.write_pd_dataframe_github(
            base_path=collection.base_path,
            path=collection.path,
            df=empty_df,
            format=collection.format,
            mode="overwrite",
            message=f"Creating empty folder for collection '{collection.name}'",
        )
        logger.info(f"📁 Folder for collection '{collection.name}' created.")

    @refresh_collection_list
    def create_collection(self, collection: Collection) -> bool:
        if self.collection_exists(name=collection.name):
            logger.warning(f"⚠️ Collection '{collection.name}' already exists.")
            return False

        self.collection_list.append(collection)
        self._persist_collections()
        self.create_collection_folder(collection=collection)
        logger.info(f"✅ Collection '{collection.name}' created successfully.")
        return True

    def _persist_collections(self):
        df = pd.DataFrame([vars(c) for c in self.collection_list])
        self.git_connection.write_pd_dataframe_github(
            base_path=self.metadata_base_path,
            path=self.metadata_path,
            df=df,
            format="json",
            mode="overwrite",
            message="Updating collections metadata",
        )
        logger.info("📄 Collections metadata updated.")

    def save_dataframe(
        self,
        df: pd.DataFrame,
        collection_name: str,
        mode: str = "overwrite",
        message: str = None,
    ) -> bool:
        if message is None:
            message = f"Saving collection '{collection_name}'"

        if not self.collection_exists(collection_name):
            logger.error(f"❌ Collection '{collection_name}' does not exist.")
            return False

        collection = next(c for c in self.collection_list if c.name == collection_name)

        collection.updated_at = datetime.datetime.now().isoformat()
        self._persist_collections()

        self.git_connection.write_pd_dataframe_github(
            base_path=collection.base_path,
            path=collection.path,
            df=df,
            format=collection.format,
            mode=mode,
            message=message,
        )

        logger.info(f"✅ Data saved to collection '{collection_name}'.")
        return True

    @refresh_collection_list
    def delete_collection(self, name: str) -> bool:
        if not self.collection_exists(name):
            logger.error(f"❌ Collection '{name}' does not exist.")
            return False

        collection = next(c for c in self.collection_list if c.name == name)
        self.collection_list = [c for c in self.collection_list if c.name != name]
        self._persist_collections()

        try:
            self.git_connection.delete_from_github(
                base_path=collection.base_path,
                path=collection.path,
                message=f"Deleting collection '{name}'",
            )
            logger.info(f"✅ Collection '{name}' deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete collection '{name}': {e}")
            return False

    def delete_dataframe(self, collection_name: str) -> bool:
        if not self.collection_exists(collection_name):
            logger.error(f"❌ Collection '{collection_name}' does not exist.")
            return False

        collection = next(c for c in self.collection_list if c.name == collection_name)

        try:
            empty_df = pd.DataFrame()
            self.git_connection.write_pd_dataframe_github(
                base_path=collection.base_path,
                path=collection.path,
                df=empty_df,
                format=collection.format,
                mode="overwrite",
                message=f"Overwriting collection '{collection_name}' with empty DataFrame",
            )
            logger.info(f"✅ Collection '{collection_name}' cleared (empty DataFrame written).")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear collection '{collection_name}': {e}")
            return False

    def read_dataframe(self, collection_name: str) -> pd.DataFrame | None:
        if not self.collection_exists(collection_name):
            logger.error(f"❌ Collection '{collection_name}' does not exist.")
            return None

        collection = next(c for c in self.collection_list if c.name == collection_name)

        try:
            df = self.git_connection.read_pd_dataframe_github(
                base_path=collection.base_path,
                path=collection.path,
                format=collection.format,
            )
            logger.info(f"📥 DataFrame loaded from collection '{collection_name}'.")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to load data from collection '{collection_name}': {e}")
            return None
