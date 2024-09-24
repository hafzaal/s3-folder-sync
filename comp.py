import boto3
from mypy_boto3_s3.client import S3Client

from typing import Any

SOURCE_BUCKET : str = "b2-ncloud-prod"
DESTINATION_BUCKET : str = "b1-ncloud-dev"


def get_bucket_folders(bucket_name: str, s3_client: S3Client) -> set[str]:
    folder_paths: set[str] = set()

    response = s3_client.list_objects_v2(Bucket=bucket_name)
    if "Contents" not in response:
        print("The bucket does not contain any folders.")
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

def add_missing_folders(dest_bucket: str, missing_folders: list[str], s3_client: S3Client) -> None:
    count: int = 0
    if not missing_folders:
        print("All folders already exist in destination bucket.")
        return
    for item in missing_folders:
        s3_client.put_object(Bucket=dest_bucket, Key=item)
        count += 1
    print(f"{count} folders added to bucket:{dest_bucket}")


def main() -> None:
    s3 = boto3.client('s3')

    source_folders: set[str] = get_bucket_folders(SOURCE_BUCKET, s3)
    dest_folders: set[str] = get_bucket_folders(DESTINATION_BUCKET, s3)
    missing_folders: list[str] = compare_bucket_folders(source_folders, dest_folders)
    
    print(missing_folders)
    add_missing_folders(DESTINATION_BUCKET, missing_folders, s3)
    dest_folders = get_bucket_folders(DESTINATION_BUCKET, s3)
    missing_folders = compare_bucket_folders(source_folders, dest_folders)
    print(missing_folders)


if __name__ == "__main__":
    main()