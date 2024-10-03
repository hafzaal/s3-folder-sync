# Copy S3 Folder Structure from One Bucket to Another

This script copies the folder structure (empty folders and subfolders) from one Amazon S3 bucket to another. It does **not** copy the files within the folders—only the folder hierarchy. This tool recursively copies the folder hierarchy, ensuring that the destination bucket mirrors the source bucket's structure.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create AWS Credentials](#2-create-aws-credentials)
  - [3. Configure `config.py`](#3-configure-configpy)
  - [4. Install Dependencies](#4-install-dependencies)
  - [5. VsCode Extensions](#5-vscode-extensions)
- [Building and Running the Docker Container](#building-and-running-the-docker-container)
- [Running the Script](#running-the-script)
- [Notes](#notes)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- [Docker](https://www.docker.com/get-started). Ensure docker is installed on your machine.
- [Visual Studio Code](https://code.visualstudio.com/). Install VsCode with the [Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) extension installed.
- [Git bash](https://git-scm.com/downloads). To navigate local directories.

## Setup

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

Replace `your-username` and `your-repo-name` with your GitHub username and the repository name, respectively.

### 2. Create AWS Credentials

The script requires AWS credentials to access the source and destination S3 buckets. You need to set up AWS profiles on your host machine inside a folder called .aws in your home directory. You can manually create the `.aws` directory with config and credentials files or install AWS CLI and use the `aws configure --profile <profile-name>` command to set both profiles. The following steps manually create both files:

#### a. Create the `.aws` Directory

Create an `.aws` directory in your home folder if it doesn't already exist. Open git bash and enter the following:

```bash
mkdir -p ~/.aws
```

#### b. Create `config` and `credentials` Files

Create the `config` and `credentials` files inside the `.aws` directory:

```bash
touch ~/.aws/config
touch ~/.aws/credentials
```

#### c. Edit the `config` File

Open `~/.aws/config` in your favorite text editor and add your AWS profiles:

```ini
[profile source-profile]
region = your-source-region

[profile destination-profile]
region = your-destination-region
```

Replace `source-profile` and `destination-profile` with the names of your AWS profiles. Replace `your-source-region` and `your-destination-region` with the appropriate AWS regions (e.g., `ca-central-1`).

#### d. Edit the `credentials` File

Open `~/.aws/credentials` and add your AWS credentials:

```ini
[source-profile]
aws_access_key_id = YOUR_SOURCE_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SOURCE_SECRET_ACCESS_KEY
aws_session_token = YOUR_SOURCE_SESSION_TOKEN

[destination-profile]
aws_access_key_id = YOUR_DESTINATION_ACCESS_KEY_ID
aws_secret_access_key = YOUR_DESTINATION_SECRET_ACCESS_KEY
aws_session_token = YOUR_DESTINATION_SESSION_TOKEN
```

Replace the placeholders with your actual AWS access keys and session tokens.

> **Note:** If you don't require session tokens, you can omit the `aws_session_token` line.

### 3. Configure `config.py`

The `config.py` file contains variables that need to be set before running the script.

Open `config.py` and set the following variables:

#### AWS CLI Profiles

```python
SOURCE_AWS_PROFILE: str = "source-profile"
DESTINATION_AWS_PROFILE: str = "destination-profile"
```

Replace `"source-profile"` and `"destination-profile"` with the names of the profiles you set in the AWS `config` file.

#### AWS Bucket Names

```python
SOURCE_BUCKET: str = "your-source-bucket-name"
DESTINATION_BUCKET: str = "your-destination-bucket-name"
```

Replace `"your-source-bucket-name"` and `"your-destination-bucket-name"` with the names of the appropriate S3 buckets.

#### Root Directory Names (Optional)

If you want to specify a root directory in your buckets, set `IS_CUSTOM_ROOT` to `True` and specify the `NAME`:

```python
SOURCE_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=True, NAME="your/source/root/")
DESTINATION_DIRECTORY = Custom_Root(IS_CUSTOM_ROOT=True, NAME="your/destination/root/")
```

If you don't need a custom root, leave `IS_CUSTOM_ROOT` as `False` and `NAME` as an empty string.

> **Note:** Ensure that the root directories are specified correctly. If `IS_CUSTOM_ROOT` is `True`, `NAME` must not be empty, and vice versa.


### 4. Install Dependencies

The Dockerfile automatically installs the necessary Python dependencies listed in `requirements.txt`. If you need to update dependencies, modify requirements.txt and rebuild the container.

### 5. VsCode Extensions

The devcontainer.json file installs some extensions to help with development inside the container. These are defined under the `extensions` section of the file. Make sure to use an extension's unique identifier (found in VsCode marketplace listing) when adding it to the list of extensions.

## Building and Running the Docker Container

The project uses Docker and VSCode's devcontainer extension to set up the Python environment.

### 1. Open the Project in VSCode

Open the project folder in Visual Studio Code.

### 2. Reopen in Container

When you open the project, VSCode should detect the `devcontainer` configuration and prompt you to reopen the folder in a container. Click on **"Reopen in Container"** when prompted.

If not prompted, you can manually reopen the folder in a container:

- Press `F1` to open the command palette.
- Type `Dev-Containers: Reopen in Container` and select it.

### 3. Wait for the Container to Build

The first time you build the container, it may take a few minutes as Docker builds the image specified in the `Dockerfile`.

### 4. Verify the Python Environment

Once the container is running, verify that the Python environment is set up correctly:

- Open a terminal in VSCode (View > Terminal) or by pressing ``Ctrl + ` ``.
- Run:

  ```bash
  which python3
  ```

  It should point to `/opt/python_dev/bin/python3`.

## Running the Script

With the container running and the environment set up, you can run the script.

1. Open a terminal in VSCode (if not already open).

2. Ensure you're in the project root directory.

3. Run the script:

   ```bash
   python3 comp.py
   ```

The script will:

- Retrieve all folders and subfolders from the source and destination S3 buckets.
- Compare the folder structure of source bucket with the destination S3 bucket.
- Add any missing folders to the destination S3 bucket.
- Print out the list of folders that were added.

## Notes

- **AWS Credentials and Profiles**: The script uses the AWS profiles specified in `config.py`. Ensure that the profiles match those in your AWS `config` and `credentials` files.

- **Permissions**: Make sure that the AWS credentials used have the necessary permissions to list and put objects in the respective S3 buckets.

- **Session Tokens**: If your AWS credentials require session tokens (e.g., for temporary credentials), make sure to include them in the `credentials` file.

- **Using Bash**: All commands and scripts are intended to be run using Bash. Ensure your terminal environment supports Bash.

- **Using different credential files**: The `devcontainer.json` file allows the user to set custom `config` and `credential` to minimize exposure of all credentials. Change the `AWS_CONFIG_FILE` and `AWS_SHARED_CREDENTIALS_FILE` variables in `containerEnv` to point to the desired files.

## Troubleshooting

- **AWS Credentials Not Found**: If the script cannot find AWS credentials, ensure that the `.aws` directory and its files are correctly mounted into the Docker container. The `devcontainer.json` file mounts the host's `.aws` directory into the container.

- **Incorrect Root Directories**: If you receive an error saying `The source or destination directories aren't specified correctly`, double-check the `IS_CUSTOM_ROOT` and `NAME` variables in `config.py`.

- **Docker Build Issues**: If you encounter errors while building the Docker container, ensure that Docker is running before staring VSCode/devcontainer.

- **Python Environment Not Activated**: If you notice that the Python environment is not activated in the container, ensure that the `set_python_env.sh` script has executed correctly.