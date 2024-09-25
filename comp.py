import boto3
from mypy_boto3_s3.client import S3Client

from typing import Any

SOURCE_BUCKET: str = "b2-nc-prod"
DESTINATION_BUCKET: str = "b1-ncloud-dev"
SOURCE_PROFILE: str = "prod"
DESTINATION_PROFILE: str = "dev"


def get_bucket_folders(bucket_name: str, s3_client: S3Client) -> set[str]:
    folder_paths: set[str] = set()

    response = s3_client.list_objects_v2(Bucket=bucket_name)
    if "Contents" not in response:
        print(f"The bucket <{bucket_name}> does not contain any folders.")
        return folder_paths
    
    for obj in response["Contents"]:
        folder_path: str = obj["Key"] # pyright: ignore [reportTypedDictNotRequiredAccess]
        if folder_path.endswith('/'):
            folder_paths.add(folder_path)

    return folder_paths

def compare_bucket_folders(source_folders: set[str], dest_folders: set[str]) -> list[str]:
    missing_folders: list[str] = []

    for path in source_folders:
        if path not in dest_folders:
            missing_folders.append(path)
    
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

def list_missing_folders(missing_folders: list[str]) -> None:
    for item in missing_folders:
        print(item)

def main() -> None:
    dev_session = boto3.Session(profile_name=DESTINATION_PROFILE)
    s3_dev = dev_session.client('s3')

    prod_session = boto3.Session(profile_name=SOURCE_PROFILE)
    s3_prod = prod_session.client('s3')

    print(sync_buckets(s3_prod, s3_dev))
    print(sync_buckets(s3_prod, s3_dev))


if __name__ == "__main__":
    main()