"""Safe synchronization of the remote catalog."""

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

CATALOG_URL = (
    "https://raw.githubusercontent.com/"
    "GeneralKaos666/termux-pkg-catalog/main/catalog.json"
)
CACHE_FILE = Path(__file__).with_name("catalog_cache.json")
TIMEOUT = 8
MAX_BYTES = 2 * 1024 * 1024


class CatalogError(Exception):
    """Error while downloading, validating or saving a catalog."""


def validate_catalog(data):
    if not isinstance(data, dict):
        raise CatalogError("The remote document is not a JSON object.")

    if data.get("schema_version") != 1:
        raise CatalogError("Unsupported catalog format version.")

    version = data.get("catalog_version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise CatalogError("The catalog version is invalid.")

    packages = data.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise CatalogError("The catalog contains no valid categories.")

    if len(packages) > 200:
        raise CatalogError("The catalog exceeds the category limit.")

    for category, entries in packages.items():
        if not isinstance(category, str) or not category.strip():
            raise CatalogError("A category without a name was found.")
        if not isinstance(entries, dict) or len(entries) > 1000:
            raise CatalogError(f"Invalid category: {category}")

        for name, command in entries.items():
            if not isinstance(name, str) or not name.strip():
                raise CatalogError(f"Unnamed package in {category}.")
            if not isinstance(command, str) or not command.strip():
                raise CatalogError(f"Invalid command for {name}.")
            if len(name) > 120 or len(command) > 500:
                raise CatalogError(f"Entry too long: {name}")

    return data


def load_cache():
    """Load the last accepted catalog; return None when it is not valid."""
    try:
        with CACHE_FILE.open("r", encoding="utf-8") as file:
            return validate_catalog(json.load(file))
    except (OSError, json.JSONDecodeError, CatalogError):
        return None


def download_catalog():
    """Download and validate the catalog published on GitHub."""
    request = Request(
        CATALOG_URL,
        headers={"User-Agent": "Termux-Package-Catalog-AutoSync/1.0", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=TIMEOUT) as response:
            content = response.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise CatalogError("The remote catalog exceeds the allowed size.")
        data = json.loads(content.decode("utf-8"))
        return validate_catalog(data)
    except HTTPError as error:
        raise CatalogError(f"GitHub responded with HTTP {error.code}.") from error
    except URLError as error:
        raise CatalogError("Could not connect to GitHub.") from error
    except (TimeoutError, OSError) as error:
        raise CatalogError("The connection failed or timed out.") from error
    except UnicodeDecodeError as error:
        raise CatalogError("The remote catalog is not valid UTF-8.") from error
    except json.JSONDecodeError as error:
        raise CatalogError("GitHub returned invalid JSON.") from error


def save_cache(data):
    """Save the accepted catalog through an atomic replacement."""
    validate_catalog(data)
    temp_file = CACHE_FILE.with_suffix(".json.tmp")
    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        os.replace(temp_file, CACHE_FILE)
    except OSError as error:
        try:
            temp_file.unlink(missing_ok=True)
        except OSError:
            pass
        raise CatalogError("Could not save the local catalog.") from error
