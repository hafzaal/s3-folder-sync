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
SOURCE_AWS_PROFILE: str = "prod"
## DESTINATION_AWS_PROFILE: The AWS profile, created using AWS CLI, for the destination bucket.
DESTINATION_AWS_PROFILE: str = "dev"

#######################################################################

##### AWS Bucket Names
## Source Bucket: The bucket where the folders will be copied from.
SOURCE_BUCKET: str = "b2-nc-prod"
## Destination Bucket: The bucket where folders will be copied to.
DESTINATION_BUCKET: str = "b1-ncloud-dev"


#######################################################################

##### Root Directory Names
# Use empty string for root.
# The IS_CUSTOM_ROOT bool must be set alongside the NAME variable.
## Source Directory: The root directory where the folder search will begin..
SOURCE_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=False, NAME="CDSP Help - PSDI Aide/")
## Destination Directory: The directory where folders will be copied to.
DESTINATION_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=True, NAME="Test2/Testing/")

#######################################################################