import os
import shutil
import json
from datetime import datetime

def ensure_directory(path):
    """Ensure the directory exists; create it if it doesn't."""
    if not os.path.exists(path):
        os.makedirs(path)

def delete_all_backups(backup_base_path):
    """Delete all contents in the backup directory."""
    if os.path.exists(backup_base_path):
        print(f"Deleting all previous backups in the directory: {backup_base_path}")
        shutil.rmtree(backup_base_path)
        # Recreate the backup base directory after deletion
        os.makedirs(backup_base_path)

def delete_all_except_version_and_script(update_path):
    """Delete all files and folders in the update directory except version.txt and updatescript.py."""
    for item in os.listdir(update_path):
        item_path = os.path.join(update_path, item)
        if os.path.isfile(item_path) and item not in ["version.txt", "updatescript.py"]:
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

def backup_and_update(src_folder, dest_folder, backup_folder):
    """Backup and update files from source to destination folder."""
    ensure_directory(backup_folder)

    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)
        backup_path = os.path.join(backup_folder, item)

        if os.path.isfile(src_path):
            if os.path.exists(dest_path):
                # Backup the existing file to the versioned backup folder
                shutil.move(dest_path, backup_path)

            # Copy the new file to the destination
            shutil.copy2(src_path, dest_path)

        elif os.path.isdir(src_path):
            # Recursively handle directories
            backup_and_update(src_path, dest_path, backup_path)

def load_json_config(config_path):
    """Load the JSON configuration from a file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def get_version_from_credentials(credentials_path):
    """Get the version from the credentials.json file."""
    with open(credentials_path, 'r') as f:
        credentials = json.load(f)
    return credentials.get("server", {}).get("version", "Unknown Version")

def main():
    paths_config_path = "/home/debian/update/paths_config.json"  # Path to your new JSON file
    credentials_path = "/home/debian/Log/credentials.json"  # Path to the credentials JSON

    # Load paths configuration
    config = load_json_config(paths_config_path)
    base_update_path = config.get("base_update_path", "/home/debian/update")  # Default if not specified
    paths = config.get("paths", {})

    # Extract version from credentials file
    version = get_version_from_credentials(credentials_path)
    print(f"Starting update process for version {version}.")

    # Define the backup base path
    backup_base_path = "/home/debian/backup"

    # Delete all previous backups in the backup folder
    delete_all_backups(backup_base_path)

    # Process each directory in the JSON configuration
    for folder, paths_info in paths.items():
        src = paths_info.get("src")
        dest = paths_info.get("dest")

        if src and dest:
            print(f"Updating {folder} from {src} to {dest}.")
            # Define the versioned backup directory
            versioned_backup_path = os.path.join(backup_base_path, version, folder)
            ensure_directory(versioned_backup_path)

            # Backup and update the folder
            backup_and_update(src, dest, versioned_backup_path)
        else:
            print(f"Source or destination for {folder} is not properly defined. Skipping {folder}.")

    # Clean up the update directory, keeping only version.txt and updatescript.py
    delete_all_except_version_and_script(base_update_path)
    print("Cleaned up update directory, keeping only version.txt and updatescript.py.")

    print("Update completed successfully.")

if __name__ == "__main__":
    main()
