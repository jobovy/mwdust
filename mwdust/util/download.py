import os
import pathlib
import shutil
import requests
import tqdm

dust_dir = os.environ.get("DUST_DIR")
if dust_dir is None:
    dust_dir = os.path.expanduser(os.path.join("~", ".mwdust"))
if not os.path.exists(dust_dir):
    os.mkdir(dust_dir)

def downloader(url, fullfilename, name, test=False):
    """
    url: URL of data file
    fullfilename: full local path
    name: name of the task
    """
    user_agent = "Mozilla/5.0"
    r = requests.get(url, stream=True, allow_redirects=True, verify=True, headers={"User-Agent": user_agent})
    if r.status_code == 404:
        raise ConnectionError(f"Cannot find {name} data file at {url}")
    r.raise_for_status()  # Will only raise for 4xx codes
    if not test:
        file_size = int(r.headers.get('Content-Length', 0))
        path = pathlib.Path(fullfilename).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)

        # r.raw.read
        with tqdm.tqdm.wrapattr(r.raw, "read", total=file_size, desc=f"Download {name}") as r_raw:
            with path.open("wb") as f:
                shutil.copyfileobj(r_raw, f)
