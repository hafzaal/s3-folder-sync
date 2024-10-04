from typing import NamedTuple

#######################################################################
##### Classes

# A NamedTuple for holding variables that help set a custom root directory.
class Custom_Root(NamedTuple):
    IS_CUSTOM_ROOT: bool
    NAME: str

#######################################################################

##### AWS CLI Profiles
# AWS profiles can belong to different or the same AWS accounts.
# If using the same account for both buckets, set both profiles to the same value.
## SOURCE_AWS_PROFILE: The AWS profile for accessing the source bucket.
SOURCE_AWS_PROFILE: str = ""
## DESTINATION_AWS_PROFILE: The AWS profile for accessing the destination bucket.
DESTINATION_AWS_PROFILE: str = ""

#######################################################################

##### AWS Bucket Names
## SOURCE_BUCKET: The name of the source bucket from which folders will be copied.
SOURCE_BUCKET: str = ""
## DESTINATION_BUCKET: The name of the destination bucket to which folders will be copied.
DESTINATION_BUCKET: str = ""


#######################################################################

##### Root Directory Names
# The root directory specifies the starting point within the bucket for any operations.
# By default, it's set to an empty string "", which refers to the bucket's root level.
#
# To use a custom root directory within a bucket:
#   - Set IS_CUSTOM_ROOT to True.
#   - Provide the NAME of the custom root directory.
# Both fields must be updated together to correctly specify the custom root.
#
# Important:
# - The IS_CUSTOM_ROOT and NAME variables must be changed together; setting one without the other may lead to incorrect behavior.
# - Ensure that the NAME provided corresponds to an existing directory within the bucket.
#   - If a destination root directory does not exist. AWS will create a new folder for that root directory.
# - The SOURCE_DIRECTORY and DESTINATION_DIRECTORY can be set independently; you can have a custom root in one bucket and use the root level in another.
#
# Examples:
# - To use the bucket's root level:
#     Custom_Root(IS_CUSTOM_ROOT=False, NAME="")
# - To transfer files to a custom directory inside the destination bucket e.g. "/folder/subfolder/":
#     Custom_Root(IS_CUSTOM_ROOT=True, NAME="folder/subfolder/")
#
## SOURCE_DIRECTORY: Custom_Root instance specifying the root directory in the source bucket.
SOURCE_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=False, NAME="")
## DESTINATION_DIRECTORY: Custom_Root instance specifying the root directory in the destination bucket.
DESTINATION_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=False, NAME="")

#######################################################################