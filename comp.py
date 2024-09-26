import boto3
from mypy_boto3_s3.client import S3Client

from typing import Any

SOURCE_BUCKET: str = "b2-nc-prod"
DESTINATION_BUCKET: str = "b1-ncloud-dev"
SOURCE_PROFILE: str = "prod"
DESTINATION_PROFILE: str = "dev"

# Initial call is with prefix "" and delimiter
# From initial call, we will get a response that will contain CommonPrefixes, that will contain all the subfolders.
# We then go through each common prefix/subfolder and make the call again but this time, prefix = commonPrefix and delim = /
# while, response.commonprefix isn't empty
# We keep doing this until we have all the subfolders.

def lookup_subfolders(current_folder: str, bucket_name: str, s3_client: S3Client, folder_paths: set[str]) -> None:
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=current_folder, Delimiter='/'):
        subfolders = page.get("CommonPrefixes", None) # pyright: ignore [reportTypedDictNotRequiredAccess]
        if subfolders is None:
            return
        for folder in subfolders:
            folder_name: str = folder["Prefix"] # pyright: ignore [reportTypedDictNotRequiredAccess]
            folder_paths.add(folder_name)
            lookup_subfolders(folder_name, bucket_name, s3_client, folder_paths)


def get_bucket_folders(bucket_name: str, s3_client: S3Client) -> set[str]:
    folder_paths: set[str] = set()
    lookup_subfolders("", bucket_name, s3_client, folder_paths)
    return folder_paths

def compare_bucket_folders(source_folders: set[str], dest_folders: set[str]) -> list[str]:
    missing_folders: list[str] = list(source_folders - dest_folders)
    return missing_folders

def add_missing_folders(destination_bucket: str, missing_folders: list[str], dest_s3_client: S3Client) -> None:
    count: int = 0
    if not missing_folders:
        print(f"All folders already exist in destination bucket <{destination_bucket}>.")
        return
    for item in missing_folders:
        dest_s3_client.put_object(Bucket=destination_bucket, Key=item)
        count += 1
    print(f"{count} folders added to bucket:{destination_bucket}")


def sync_buckets(source_s3_client: S3Client, destination_s3_client: S3Client) -> list[str]:
    source_folders: set[str] = get_bucket_folders(SOURCE_BUCKET, source_s3_client)
    dest_folders: set[str] = get_bucket_folders(DESTINATION_BUCKET, destination_s3_client)
    missing_folders: list[str] = compare_bucket_folders(source_folders, dest_folders)
    
    add_missing_folders(DESTINATION_BUCKET, missing_folders, destination_s3_client)
    return missing_folders

def list_folders(folders: list[str]) -> None:
    for folder in folders:
        print(folder)

def main() -> None:
    dev_session = boto3.Session(profile_name=DESTINATION_PROFILE)
    s3_dev = dev_session.client('s3')

    prod_session = boto3.Session(profile_name=SOURCE_PROFILE)
    s3_prod = prod_session.client('s3')

    missing_folders: list[str] = sync_buckets(s3_prod, s3_dev)
    list_folders(missing_folders)
    #print(get_bucket_folders(SOURCE_BUCKET, s3_prod))


if __name__ == "__main__":
    main()