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

def main() -> None:
    s3 = boto3.client('s3')


    ##
    ## Get names of all objects in a bucket
    ##
    # response = s3.list_objects_v2(Bucket=DEV_BUCKET_NAME)
    # if "Contents" in response:
    #     for obj in response["Contents"]:
    #         print(obj["Key"]) # pyright: ignore [reportTypedDictNotRequiredAccess]


    ##
    ## Get names of all objects that are folders in a bucket
    ##
    # response = s3.list_objects_v2(Bucket=PROD_BUCKET_NAME)
    # if "Contents" in response:
    #     for obj in response["Contents"]:
    #         name: str = obj["Key"] # pyright: ignore [reportTypedDictNotRequiredAccess]
    #         if name.endswith('/'):
    #             print(name)


    #
    # List all buckets
    #
    # response = s3.list_buckets()
    # for bucket in response["Buckets"]:
    #     print(bucket["Name"]) # pyright: ignore [reportTypedDictNotRequiredAccess]


if __name__ == "__main__":
    main()