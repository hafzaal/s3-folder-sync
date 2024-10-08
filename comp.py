import boto3
from mypy_boto3_s3.client import S3Client
from config import *

def lookup_subfolders(current_folder: str, bucket_name: str, s3_client: S3Client, folder_paths: set[str], root_folder: str) -> None:
    """A recursive function that is used to find all folders and subfolders in a bucket.

    Args:
        current_folder (str): The current folder where the method searches for further subfolders.
        bucket_name (str): The bucket which contains folders that need to be retrieved.
        s3_client (S3Client): The client whose bucket needs to be searched.
        folder_paths (set[str]): A set containing all the currently found folders/paths.
        root_folder (str): The root folder where the search is initiated.
    """
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=current_folder, Delimiter='/'):
        subfolders = page.get("CommonPrefixes", None) # pyright: ignore [reportTypedDictNotRequiredAccess]
        if subfolders is None:
            return
        for folder in subfolders:
            folder_name: str = folder["Prefix"] # pyright: ignore [reportTypedDictNotRequiredAccess]
            if root_folder and root_folder == DESTINATION_DIRECTORY.NAME:
                folder_paths.add(folder_name.removeprefix(root_folder))
            else:
                folder_paths.add(folder_name)
            lookup_subfolders(folder_name, bucket_name, s3_client, folder_paths, root_folder)

def get_bucket_folders(starting_folder: str, bucket_name: str, s3_client: S3Client) -> set[str]:
    """Gets all folders from inside a bucket by recursively searching through each folder based on starting folder specified.

    Args:
        starting_folder (str): The folder where the search begins. Pass empty string to denote root of bucket, otherwise specify the folder name.
        bucket_name (str): The bucket which contains folders that need to be retrieved.
        s3_client (S3Client): The client whose bucket needs to be searched.

    Returns:
        set[str]: _description_
    """
    folder_paths: set[str] = set()
    root_folder: str = starting_folder
    lookup_subfolders(starting_folder, bucket_name, s3_client, folder_paths, root_folder)
    return folder_paths

def compare_bucket_folders(source_folders: set[str], dest_folders: set[str]) -> list[str]:
    """Compares two sets of folders and finds the difference between them.

    Args:
        source_folders (set[str]): A set of strings denoting folder names/path of all folders in the source bucket.
        dest_folders (set[str]): A set of strings denoting folder names/path of all folders in the destination bucket.

    Returns:
        list[str]: A list that contains folders present in the source bucket but missing from the destination bucket.
    """
    missing_folders: list[str] = list(source_folders - dest_folders)
    return missing_folders

def add_missing_folders(bucket_name: str, missing_folders: list[str], s3_client: S3Client) -> None:
    """Add missing folders to a client's bucket.

    Args:
        bucket_name (str): The name of the bucket to which folders will be added.
        missing_folders (list[str]): The list of folder names/path which are missing in the bucket.
        s3_client (S3Client): The client whose bucket the folders will be copied to.
    """
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
    """ Copies and Syncs folders from a source bucket to destination bucket.

    Args:
        source_s3_client (S3Client): A client referencing the source bucket. Data will be copied from this client's bucket.
        destination_s3_client (S3Client): A client referencing the destination bucket. Data will be copied to this client's bucket.

    Returns:
        list[str]: Returns a list of strings denoting the paths/folder names of every folder that was present in source folder
        but is missing in the destination folder.
    """
    print("Getting source bucket folders...")
    source_folders: set[str] = get_bucket_folders(starting_folder=SOURCE_DIRECTORY.NAME,
                                                  bucket_name=SOURCE_BUCKET,
                                                  s3_client=source_s3_client)
    print("Getting destination bucket folders...")
    dest_folders: set[str] = get_bucket_folders(starting_folder=DESTINATION_DIRECTORY.NAME,
                                                bucket_name=DESTINATION_BUCKET,
                                                s3_client=destination_s3_client)
    print("Finding missing folders...")
    missing_folders: list[str] = compare_bucket_folders(source_folders, dest_folders)
    
    print("Adding missing folders to destination bucket...")
    add_missing_folders(DESTINATION_BUCKET, missing_folders, destination_s3_client)
    return missing_folders

def print_missing_folders(folders: list[str]) -> None:
    """Prints the list of folders specified by the user in a sorted order.

    Args:
        folders (list[str]): A list containing folder names.
    """
    if not folders:
        print("No folders to print. The folders list is empty.")
        return
    print("The following folders were added to the destination bucket:")
    folders.sort()
    for folder in folders:
        print(folder)

def are_root_directories_valid() -> bool:
    """Checks whether the root directories specified in the config file are setup correctly.
    The root directory NamedTuple requires both variables to be set correctly.
    Returns:
        bool: True if the root directory are valid and have correct values. False if the
        variables have incorrect values.
    """
    if ((not SOURCE_DIRECTORY.IS_CUSTOM_ROOT and SOURCE_DIRECTORY.NAME or
         SOURCE_DIRECTORY.IS_CUSTOM_ROOT and not SOURCE_DIRECTORY.NAME) or
        (not DESTINATION_DIRECTORY.IS_CUSTOM_ROOT and DESTINATION_DIRECTORY.NAME or
         DESTINATION_DIRECTORY.IS_CUSTOM_ROOT and not DESTINATION_DIRECTORY.NAME)):
        return False
    return True

def main() -> None:
    if not are_root_directories_valid():
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