'''
==========================================================
Author: road2nowhere (https://road2nowhere.neocities.org/)
Created at: 2026-08-26
==========================================================

## Summary

Tool to automatically sync local files to a Neocities site
using the Neocities API.

## Usage

```sh
$ python neocities-sync.py
```

Will prompt for your Neocities sitename and password to
generate an API key. The API key will be saved in a file
named .neocities in the current working directory. The script
will then compare the local files with the remote files on
your Neocities site and display a summary of the changes.

You will be prompted to confirm before any changes are made
to your Neocities site.

## Warnings

- The script will save your API key at ./.neocities in the 
current working directory after the first login. DO NOT
publish this file or share it with anyone. Treat it like a
password.

- The script will automatically create, upload and delete 
files on your Neocities site after user confirmation. MAKE 
SURE you have a backup of what is currently on your site 
before running this script.

## Future improvements:

- Support for syncing partial changes.

==========================================================
'''

import requests
import getpass
import hashlib
from pathlib import Path


CONFIG_DIR = Path.cwd()
CONFIG_API = Path(".neocities")
NEOCITIES_API = "https://neocities.org"

# Folders that will not be synced to Neocities FS.
ignored_folders = {
    ".git",
    "node_modules",
    "__pycache__",
}

# Change here the extensions of the files you want to deploy. By default, it includes common web file types.
allowed_extensions = {
    ".html",
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".txt",
    ".avif"
}

cwd = Path.cwd()


def get_api_key():
    api_key_path = CONFIG_DIR / CONFIG_API

    if api_key_path.exists():
        print("Retrieving saved API key...")
        return api_key_path.read_text().strip()

    print("No API key found. Generating one...")

    sitename = input("Sitename: ")
    password = getpass.getpass("Password: ")

    response = requests.get(
        url=f"{NEOCITIES_API}/api/key",
        auth=(sitename, password),
    )
    response.raise_for_status()

    result = response.json()

    if result.get("result") != "success":
        raise RuntimeError(
            result.get(
                "message",
                "Failed to generate API key.",
            )
        )

    api_key = result["api_key"]

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    api_key_path.write_text(api_key)
    api_key_path.chmod(0o600)

    print("API key saved.")

    return api_key


def get_auth_header():
    return {
        "Authorization": f"Bearer {get_api_key()}"
    }


def sha1_file(path, chunk_size=1024 * 1024):
    digest = hashlib.sha1()

    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def list_local_files():
    files = []

    for p in cwd.rglob("*"):
        if (
            p.is_file()
            and p.suffix.lower() in allowed_extensions
            and not set(p.parts).intersection(ignored_folders)
        ):
            files.append(
                {
                    "path": str(p.relative_to(cwd)),
                    "sha1_hash": sha1_file(p),
                    "size": p.stat().st_size,
                }
            )

    return files


def list_remote_files(auth_header):
    response = requests.get(
        url=f"{NEOCITIES_API}/api/list",
        headers=auth_header,
    )
    response.raise_for_status()

    result = response.json()

    if result.get("result") != "success":
        raise RuntimeError(
            result.get(
                "message",
                "Failed to list remote files.",
            )
        )

    return result["files"]


def compare_files(local_files, remote_files):
    local_by_path = {
        file["path"]: file
        for file in local_files
    }

    remote_by_path = {
        file["path"]: file
        for file in remote_files
        if not file["is_directory"]
    }

    local_paths = set(local_by_path)
    remote_paths = set(remote_by_path)

    added_files = [
        {
            "path": path,
            "size": local_by_path[path]["size"],
        }
        for path in sorted(
            local_paths - remote_paths
        )
    ]

    tracked_files = [
        {
            "path": path,
            "local_sha1_hash":
                local_by_path[path]["sha1_hash"],
            "remote_sha1_hash":
                remote_by_path[path]["sha1_hash"],
            "local_size":
                local_by_path[path]["size"],
            "remote_size":
                remote_by_path[path].get("size", 0),
        }
        for path in sorted(
            local_paths & remote_paths
        )
    ]

    deleted_files = [
        {
            "path": path,
            "size":
                remote_by_path[path].get("size", 0),
        }
        for path in sorted(
            remote_paths - local_paths
        )
    ]

    return (
        added_files,
        tracked_files,
        deleted_files,
    )


def get_modified_files(tracked_files):
    return [
        file
        for file in tracked_files
        if (
            file["local_sha1_hash"]
            != file["remote_sha1_hash"]
        )
    ]


def format_size(size):
    size = float(size)

    for unit in (
        "B",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
    ):
        if size < 1024 or unit == "TiB":
            if unit == "B":
                return f"{int(size)} {unit}"

            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} TiB"


def get_remote_storage_summary(remote_files):
    files = [
        file
        for file in remote_files
        if not file["is_directory"]
    ]

    total_size = sum(
        file.get("size", 0)
        for file in files
    )

    return len(files), total_size


def print_storage_summary(remote_files):
    file_count, total_size = (
        get_remote_storage_summary(
            remote_files
        )
    )

    print(
        f"Storage: {format_size(total_size)} "
        f"across {file_count} files."
    )


def print_changes(
    added_files,
    modified_files,
    deleted_files,
):
    rows = []

    for file in added_files:
        rows.append(
            (
                "ADD",
                format_size(file["size"]),
                file["path"],
            )
        )

    for file in modified_files:
        old_size = format_size(
            file["remote_size"]
        )
        new_size = format_size(
            file["local_size"]
        )

        rows.append(
            (
                "MOD",
                f"{old_size} -> {new_size}",
                file["path"],
            )
        )

    for file in deleted_files:
        rows.append(
            (
                "DEL",
                format_size(file["size"]),
                file["path"],
            )
        )

    if not rows:
        return

    change_width = max(
        len("CHANGE"),
        *(len(row[0]) for row in rows),
    )

    size_width = max(
        len("SIZE"),
        *(len(row[1]) for row in rows),
    )

    print()

    print(
        f"{'CHANGE':<{change_width}}  "
        f"{'SIZE':<{size_width}}  "
        f"PATH"
    )

    print(
        f"{'-' * change_width}  "
        f"{'-' * size_width}  "
        f"----"
    )

    for change, size, path in rows:
        print(
            f"{change:<{change_width}}  "
            f"{size:<{size_width}}  "
            f"{path}"
        )


def print_progress(
    current,
    total,
    path="",
    width=30,
):
    if total == 0:
        return

    ratio = current / total
    filled = int(width * ratio)

    bar = (
        "#" * filled
        + "-" * (width - filled)
    )

    print(
        f"\rUploading "
        f"[{bar}] "
        f"{current:>{len(str(total))}}/{total} "
        f"{ratio:6.1%}  "
        f"{path}"
        f"\033[K",
        end="",
        flush=True,
    )


def upload_files(files, auth_header):
    if not files:
        return []

    upload_results = []
    total = len(files)

    print()
    print_progress(0, total)

    for index, file in enumerate(
        files,
        start=1,
    ):
        path = file["path"]
        local_path = cwd / path

        print_progress(
            index - 1,
            total,
            path,
        )

        with local_path.open("rb") as local_file:
            response = requests.post(
                url=f"{NEOCITIES_API}/api/upload",
                headers=auth_header,
                files={
                    path: (
                        local_path.name,
                        local_file,
                    )
                },
            )

        response.raise_for_status()

        result = response.json()

        if result.get("result") != "success":
            raise RuntimeError(
                result.get(
                    "message",
                    f"Failed to upload {path}.",
                )
            )

        upload_results.append(result)

        print_progress(
            index,
            total,
            path,
        )

    print()

    return upload_results


def create_directories(local_files, remote_files, auth_header):
    remote_directories = {
        file["path"].strip("/")
        for file in remote_files
        if file["is_directory"]
    }
    required_directories = set()

    for file in local_files:
        parent = Path(file["path"]).parent

        while parent != Path("."):
            required_directories.add(parent.as_posix())
            parent = parent.parent

    directories_to_create = sorted(
        required_directories - remote_directories,
        key=lambda path: (path.count("/"), path),
    )

    for index, path in enumerate(directories_to_create):
        print(f"[CREATE DIRECTORY]:\t{path}")

        response = requests.post(
            url=f"{NEOCITIES_API}/api/create_directory",
            headers=auth_header,
            data={"path": path},
        )
        response.raise_for_status()

        result = response.json()

        if result.get("result") != "success":
            raise RuntimeError(
                result.get(
                    "message",
                    f"Failed to create directory {path}.",
                )
            )


def delete_files(files, auth_header):
    if not files:
        return None

    print("\nDeleting files:")

    for file in files:
        print(f"  {file['path']}")

    delete_data = [
        ("filenames[]", file["path"])
        for file in files
    ]

    response = requests.post(
        url=f"{NEOCITIES_API}/api/delete",
        headers=auth_header,
        data=delete_data,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("result") != "success":
        raise RuntimeError(
            result.get(
                "message",
                "Failed to delete files.",
            )
        )

    return result


def main():
    print("Neocities Deploy")
    print(f"Directory: {cwd}")

    try:
        auth_header = get_auth_header()

        local_files = list_local_files()
        remote_files = list_remote_files(
            auth_header
        )

        (
            added_files,
            tracked_files,
            deleted_files,
        ) = compare_files(
            local_files,
            remote_files,
        )

        modified_files = get_modified_files(
            tracked_files
        )

        if not (
            added_files
            or modified_files
            or deleted_files
        ):
            print(
                "\nNo changes to deploy. "
                "Site is already up to date."
            )

            print_storage_summary(
                remote_files
            )

            return

        print_changes(
            added_files,
            modified_files,
            deleted_files,
        )

        print(
            f"\nSummary: "
            f"{len(added_files)} added, "
            f"{len(modified_files)} modified, "
            f"{len(deleted_files)} deleted."
        )

        confirm = input(
            "\nProceed with deployment? [y/N]: "
        ).strip().lower()

        if confirm not in {"y", "yes"}:
            print("Deployment aborted.")
            return

        create_directories(
            local_files,
            remote_files,
            auth_header,
        )

        upload_files(
            added_files + modified_files,
            auth_header,
        )

        delete_files(
            deleted_files,
            auth_header,
        )

        print(
            "\nDeployment completed successfully."
        )

        print(
            f"Summary: "
            f"{len(added_files)} added, "
            f"{len(modified_files)} modified, "
            f"{len(deleted_files)} deleted."
        )

    except (
        requests.RequestException,
        RuntimeError,
    ) as exc:
        print(
            f"\nDeployment failed: {exc}"
        )
        raise SystemExit(1)


if __name__ == "__main__":
    main()