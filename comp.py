import boto3
from mypy_boto3_s3.client import S3Client
from typing import NamedTuple

class Custom_Root(NamedTuple):
    IS_CUSTOM_ROOT: bool
    NAME: str

SOURCE_AWS_PROFILE: str = "prod"
DESTINATION_AWS_PROFILE: str = "dev"

SOURCE_BUCKET: str = "b2-nc-prod"
DESTINATION_BUCKET: str = "b1-ncloud-dev"

SOURCE_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=False, NAME="")
DESTINATION_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=False, NAME="")

def lookup_subfolders(current_folder: str, bucket_name: str, s3_client: S3Client, folder_paths: set[str], root_folder: str) -> None:
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=current_folder, Delimiter='/'):
        subfolders = page.get("CommonPrefixes", None) # pyright: ignore [reportTypedDictNotRequiredAccess]
        if subfolders is None:
            return
        for folder in subfolders:
            folder_name: str = folder["Prefix"] # pyright: ignore [reportTypedDictNotRequiredAccess]
            if root_folder == DESTINATION_DIRECTORY.NAME:
                folder_paths.add(folder_name.removeprefix(root_folder))
            else:
                folder_paths.add(folder_name)
            lookup_subfolders(folder_name, bucket_name, s3_client, folder_paths, root_folder)

def get_bucket_folders(starting_folder: str, bucket_name: str, s3_client: S3Client, root_folder: str) -> set[str]:
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
        if DESTINATION_DIRECTORY.IS_CUSTOM_ROOT:
            folder_name = f"{DESTINATION_DIRECTORY.NAME}{folder_name}"
        s3_client.put_object(Bucket=bucket_name, Key=folder_name)
        count += 1
    print(f"{count} folders added to bucket:{bucket_name}")

def sync_buckets(source_s3_client: S3Client, destination_s3_client: S3Client) -> list[str]:
    print("Getting source bucket folders...")
    source_folders: set[str] = get_bucket_folders(starting_folder=SOURCE_DIRECTORY.NAME,
                                                  bucket_name=SOURCE_BUCKET,
                                                  s3_client=source_s3_client,
                                                  root_folder=SOURCE_DIRECTORY.NAME)
    print("Getting destination bucket folders...")
    dest_folders: set[str] = get_bucket_folders(starting_folder=DESTINATION_DIRECTORY.NAME,
                                                bucket_name=DESTINATION_BUCKET,
                                                s3_client=destination_s3_client,
                                                root_folder=DESTINATION_DIRECTORY.NAME)
    print("Finding missing folders...")
    missing_folders: list[str] = compare_bucket_folders(source_folders, dest_folders)
    
    print("Adding missing folders to destination bucket...")
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

def are_valid_directories() -> bool:
    if ((not SOURCE_DIRECTORY.IS_CUSTOM_ROOT and SOURCE_DIRECTORY.NAME or
         SOURCE_DIRECTORY.IS_CUSTOM_ROOT and not SOURCE_DIRECTORY.NAME) or
        (not DESTINATION_DIRECTORY.IS_CUSTOM_ROOT and DESTINATION_DIRECTORY.NAME or
         DESTINATION_DIRECTORY.IS_CUSTOM_ROOT and not DESTINATION_DIRECTORY.NAME)):
        return False
    return True

def main() -> None:
    if not are_valid_directories():
        print("The source or destination directories aren't specified correctly. Check directory variables and try again.")
        return
    dev_session = boto3.Session(profile_name=DESTINATION_AWS_PROFILE)
    s3_dev = dev_session.client('s3')

    prod_session = boto3.Session(profile_name=SOURCE_AWS_PROFILE)
    s3_prod = prod_session.client('s3')

    missing_folders: list[str] = sync_buckets(s3_prod, s3_dev)
    print_missing_folders(missing_folders)

if __name__ == "__main__":
    main()