import subprocess
import base64
import requests
from pathlib import Path
import pandas as pd
from typing import Optional
import io
import logging

# Logger setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class GitConnection:
    def __init__(
        self,
        repo_url: str,
        username: str,
        token: str,
        local_path: Optional[str] = None,
        branch: str = "main",
        email: Optional[str] = None,
    ):
        self.repo_url = repo_url
        self.username = username
        self.token = token
        self.branch = branch
        self.email = email or f"{username}@users.noreply.github.com"
        self._parse_repo_info()
        self.local_path = Path(local_path) if local_path else Path.cwd() / self.repo_name
        self.auth_url = f"https://{username}:{token}@github.com/{self.owner}/{self.repo_name}.git"
        logger.info(f"Git connection configured for repository '{self.repo_name}' (owner: '{self.owner}').")

    def _parse_repo_info(self):
        clean_url = self.repo_url.replace(".git", "")
        parts = clean_url.split("/")
        self.owner = parts[-2]
        self.repo_name = parts[-1]

    def _get_file_sha(self, url: str, headers: dict) -> str | None:
        response = requests.get(url, headers=headers, params={"ref": self.branch})
        if response.status_code == 200:
            return response.json().get("sha")
        return None

    def _serialize_pd_dataframe(self, dataframe: pd.DataFrame, format: str) -> str:
        if format == "csv":
            content_str = dataframe.to_csv(index=False)
        elif format == "json":
            content_str = dataframe.to_json(orient="records", lines=True)
        elif format == "parquet":
            buffer = io.BytesIO()
            dataframe.to_parquet(buffer, index=False, engine="pyarrow")
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode()
        else:
            raise ValueError(f"Unsupported format: '{format}'")
        return base64.b64encode(content_str.encode()).decode()

    def _deserialize_pd_dataframe(self, raw_bytes: bytes, format: str) -> pd.DataFrame:
        if format == "csv":
            return pd.read_csv(io.BytesIO(raw_bytes))
        elif format == "json":
            return pd.read_json(io.BytesIO(raw_bytes), lines=True)
        elif format == "parquet":
            return pd.read_parquet(io.BytesIO(raw_bytes), engine="pyarrow")
        else:
            raise ValueError(f"Unsupported format: '{format}'")

    def _upload_file_to_github(self, url: str, headers: dict, payload: dict) -> bool:
        put_response = requests.put(url, headers=headers, json=payload)
        if put_response.status_code in [200, 201]:
            return True
        logger.error(f"Failed to upload file: HTTP {put_response.status_code}")
        logger.debug(f"GitHub response: {put_response.json()}")
        return False

    def _download_file_from_github(self, url: str, headers: dict) -> bytes:
        logger.info(f"🔽 Downloading file from: {url}")
        response = requests.get(url, headers=headers, params={"ref": self.branch})
        if response.status_code == 200:
            logger.info("📦 File found in the repository.")
            content_b64 = response.json()["content"]
            return base64.b64decode(content_b64)
        raise FileNotFoundError(f"File not found at: {url}")

    def write_pd_dataframe_github(
        self,
        base_path: str,
        path: str,
        df: pd.DataFrame,
        format: str,
        mode: str,
        message: str,
    ):
        repo = f"{self.owner}/{self.repo_name}"
        final_path = f"{base_path}/{path}.{format}"
        url = f"https://api.github.com/repos/{repo}/contents/{final_path}"

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
        }

        sha = self._get_file_sha(url, headers)

        if sha and mode == "append":
            logger.info(f"📄 Append mode: reading existing data from '{final_path}'")
            raw_bytes = self._download_file_from_github(url, headers)
            df_existing = self._deserialize_pd_dataframe(raw_bytes, format)
            df = pd.concat([df_existing, df], ignore_index=True)

        content_b64 = self._serialize_pd_dataframe(df, format)

        payload = {
            "message": message,
            "branch": self.branch,
            "content": content_b64,
            "committer": {"name": self.username, "email": self.email},
            "author": {"name": self.username, "email": self.email},
        }

        if sha:
            payload["sha"] = sha

        success = self._upload_file_to_github(url, headers, payload)
        if success:
            logger.info(f"✅ File '{final_path}' successfully uploaded to GitHub.")

    def read_pd_dataframe_github(
        self, base_path: str, path: str, format: str
    ) -> pd.DataFrame:
        repo = f"{self.owner}/{self.repo_name}"
        final_path = f"{base_path}/{path}.{format}"
        url = f"https://api.github.com/repos/{repo}/contents/{final_path}"

        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
        }

        logger.info(f"📥 Reading DataFrame from '{final_path}' on GitHub...")
        raw_bytes = self._download_file_from_github(url, headers)
        df = self._deserialize_pd_dataframe(raw_bytes, format)
        logger.info(f"✅ DataFrame successfully loaded from '{final_path}'.")
        return df
