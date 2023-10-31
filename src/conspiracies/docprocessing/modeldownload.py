"""Utilities for downloading models."""

import os
import shutil
from pathlib import Path
from typing import Union

from tqdm import tqdm
from wasabi import msg

MODEL_URLS = {
    "da_coref_twitter_v1": {
        "url": "https://sciencedata.dk/shared/"
        + "f20703362e0a771f004f8ff2026afb0f?download",
        "folder_name": "da_coref_twitter_v1",
    },
}
DEFAULT_CACHE_DIR = os.getenv(
    "CONSPIRACIES_CACHE_DIR",
    os.path.join(str(Path.home()), ".conspiracies"),
)


class DownloadProgressBar(tqdm):
    def update_to(self, b: int = 1, bsize: int = 1, tsize=None) -> None:
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url: str, output_path: str) -> None:
    import urllib.request

    with DownloadProgressBar(
        unit="B",
        unit_scale=True,
        miniters=1,
        desc=url.split("/")[-1],
    ) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


def download_model(
    model: str,
    save_path: Union[Path, str, None] = None,
    force: bool = False,
    verbose: bool = True,
    open_unverified_connection: bool = False,
) -> str:
    """Download a model name from list of models.

    Args:
        model(str): Name of the model to download.
        save_path(Union[Path, str, None], optional): Path to save the model to.
            If None, the model will be saved to the default cache directory.
        force(bool, optional): If True, the model will be downloaded even if it
            already exists. Defaults to False.
        verbose(bool, optional): If True, the model will be downloaded and saved
            to the default cache directory. Defaults to True.
        open_unverified_connection (bool, optional): Should you download from an
            unverified connection. Defaults to False.

    Returns:
        str: Path to the downloaded model.
    """

    if open_unverified_connection:
        import ssl

        ssl._create_default_https_context = ssl._create_unverified_context

    if save_path is None:
        save_path = DEFAULT_CACHE_DIR

    if model not in MODEL_URLS:
        raise ValueError(
            "The model is not available."
            + f" Models available include: {list(MODEL_URLS.keys())}",
        )
    url = MODEL_URLS[model]["url"]
    path = os.path.join(save_path, MODEL_URLS[model]["folder_name"])

    # only download model if required
    if os.path.exists(path) and force is False:
        return path

    dl_path = os.path.join(save_path, "tmp.zip")
    Path(save_path).mkdir(parents=True, exist_ok=True)

    if verbose is True:
        msg.info(f"\nDownloading '{model}'")
    download_url(url, dl_path)

    shutil.unpack_archive(dl_path, save_path)  # unzip
    os.remove(dl_path)

    if verbose is True:
        msg.info(f"Model successfully downloaded to  {path}")
    return path
