import boto3
from mypy_boto3_s3.client import S3Client

from typing import Any

DEV_BUCKET_NAME : str = "b1-ncloud-dev"
PROD_BUCKET_NAME : str = "b2-ncloud-prod"


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

def compare_bucket_folders(source_folders: set[str], dest_folders: set[str], s3_client: S3Client) -> list[str]:
    missing_folders: list[str] = []

    for path in source_folders:
        if path not in dest_folders:
            missing_folders.append(path)
    
    return missing_folders

def main() -> None:
    s3 = boto3.client('s3')

    source_folders: set[str] = get_bucket_folders(PROD_BUCKET_NAME, s3)
    dest_folders: set[str] = get_bucket_folders(DEV_BUCKET_NAME, s3)
    print(compare_bucket_folders(source_folders, dest_folders, s3))

if __name__ == "__main__":
    main()