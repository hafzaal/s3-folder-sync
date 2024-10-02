import boto3
from mypy_boto3_s3.client import S3Client
from typing import NamedTuple

SOURCE_PROFILE: str = "prod"
DESTINATION_PROFILE: str = "dev"

SOURCE_BUCKET: str = "b2-nc-prod"
DESTINATION_BUCKET: str = "b1-ncloud-dev"

SET_ROOT = NamedTuple("SET_ROOT", [("SET_CUSTOM_ROOT", bool), ("NAME", str)])

SOURCE_ROOT_DIRECTORY: str = ""
SOURCE_ROOT = SET_ROOT(SET_CUSTOM_ROOT=False, NAME="")

DESTINATION_ROOT = SET_ROOT(SET_CUSTOM_ROOT=True, NAME="Test/")

#tuple[bool, str] = (True, "Test/"
from pathlib import Path

def remove_root_folder(path_str: str) -> str:
    path: Path = Path(path_str)
    parts: tuple[str, ...] = path.parts
    if len(parts) > 1:
        new_path = Path(*parts[1:])
        return str(new_path)
    else:
        return path_str

def lookup_subfolders(current_folder: str, bucket_name: str, s3_client: S3Client, folder_paths: set[str], root_folder: str="") -> None:
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=current_folder, Delimiter='/'):
        subfolders = page.get("CommonPrefixes", None) # pyright: ignore [reportTypedDictNotRequiredAccess]
        if subfolders is None:
            return
        for folder in subfolders:
            folder_name: str = folder["Prefix"] # pyright: ignore [reportTypedDictNotRequiredAccess]
            if root_folder == DESTINATION_ROOT.NAME:
                folder_paths.add(folder_name.removeprefix(root_folder))
            else:
                folder_paths.add(folder_name)
            lookup_subfolders(folder_name, bucket_name, s3_client, folder_paths, root_folder)

def get_bucket_folders(starting_folder: str, bucket_name: str, s3_client: S3Client, root_folder: str="") -> set[str]:
    folder_paths: set[str] = set()
    lookup_subfolders(starting_folder, bucket_name, s3_client, folder_paths, root_folder)
    return folder_paths

def compare_bucket_folders(source_folders: set[str], dest_folders: set[str]) -> list[str]:
    missing_folders: list[str] = list(source_folders - dest_folders)
    return missing_folders

def add_missing_folders(bucket_name: str, missing_folders: list[str], s3_client: S3Client) -> None:
    count: int = 0
    if not missing_folders:
        print(f"All folders already exist in bucket <{bucket_name}>.")
        return
    for folder_name in missing_folders:
        if DESTINATION_ROOT.SET_CUSTOM_ROOT:
            folder_name = f"{DESTINATION_ROOT.NAME}{folder_name}"
        s3_client.put_object(Bucket=bucket_name, Key=folder_name)
        count += 1
    print(f"{count} folders added to bucket:{bucket_name}")

def sync_buckets(source_s3_client: S3Client, destination_s3_client: S3Client) -> list[str]:
    source_folders: set[str] = get_bucket_folders(SOURCE_ROOT_DIRECTORY, SOURCE_BUCKET, source_s3_client, SOURCE_ROOT_DIRECTORY)
    dest_folders: set[str] = get_bucket_folders(DESTINATION_ROOT.NAME, DESTINATION_BUCKET, destination_s3_client, DESTINATION_ROOT.NAME)
    missing_folders: list[str] = compare_bucket_folders(source_folders, dest_folders)
    
    add_missing_folders(DESTINATION_BUCKET, missing_folders, destination_s3_client)
    return missing_folders

def print_missing_folders(folders: list[str]) -> None:
    if not folders:
        print("No folders to print. The folders list is empty.")
        return
    print("The following folders were added to the destination bucket:")
    folders.sort()
    for folder in folders:
        print(folder)

def main() -> None:
    dev_session = boto3.Session(profile_name=DESTINATION_PROFILE)
    s3_dev = dev_session.client('s3')

    prod_session = boto3.Session(profile_name=SOURCE_PROFILE)
    s3_prod = prod_session.client('s3')

    missing_folders: list[str] = sync_buckets(s3_prod, s3_dev)
    print_missing_folders(missing_folders)

if __name__ == "__main__":
    main()