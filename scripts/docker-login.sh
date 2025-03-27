#AWS login
#Provide the login command to AWS ECR
# Directory to clean
TARGET_DIR="/var/www/html"
TARGET_DIR_GIT="/var/www/html/.git"
# Check if the directory exists
if [ -d "$TARGET_DIR" ]; then
    echo "Target directory exists: $TARGET_DIR"
    # Remove all files and directories inside the target directory
    if ls "$TARGET_DIR"/* &> /dev/null; then
        echo "Removing all files and directories inside $TARGET_DIR"
        sudo rm -r "$TARGET_DIR"/*
    else
        echo "No files or directories to remove inside $TARGET_DIR"
    fi
else
    echo "Target directory does not exist: $TARGET_DIR"
fi
if [ -d "$TARGET_DIR_GIT" ]; then
    echo "Target directory exists: $TARGET_DIR_GIT"
    # Remove all files and directories inside the target directory
    sudo rm -r "$TARGET_DIR_GIT"
else
    echo "Target directory does not exist: $TARGET_DIR_GIT"
fi
