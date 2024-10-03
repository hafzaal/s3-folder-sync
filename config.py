from typing import NamedTuple

#######################################################################
##### Classes

# A NamedTuple for holding variables related to setting a custom root directory.
class Custom_Root(NamedTuple):
    IS_CUSTOM_ROOT: bool
    NAME: str

#######################################################################

##### AWS CLI Profiles
# The profiles can belong to different or same accounts. If using same account, set both variables to same value.
## SOURCE_AWS_PROFILE: The AWS profile, created using AWS CLI, for the source bucket.
SOURCE_AWS_PROFILE: str = ""
## DESTINATION_AWS_PROFILE: The AWS profile, created using AWS CLI, for the destination bucket.
DESTINATION_AWS_PROFILE: str = ""

#######################################################################

##### AWS Bucket Names
## Source Bucket: The bucket where the folders will be copied from.
SOURCE_BUCKET: str = ""
## Destination Bucket: The bucket where folders will be copied to.
DESTINATION_BUCKET: str = ""


#######################################################################

##### Root Directory Names
# Default/non-custom value for root directory: ""
# The IS_CUSTOM_ROOT bool must be set alongside the NAME variable.
#   If you set a custom root, set bool to True.
## Source Directory: The root directory where the folder search will begin..
SOURCE_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=False, NAME="")
## Destination Directory: The directory where folders will be copied to.
DESTINATION_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=False, NAME="")

#######################################################################