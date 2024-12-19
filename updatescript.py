import os
import shutil
import json
from datetime import datetime

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def delete_all_backups(backup_base_path):
    """Delete all contents in the backup directory."""
    if os.path.exists(backup_base_path):
        print(f"Deleting all previous backups in the directory: {backup_base_path}")
        shutil.rmtree(backup_base_path)
        # Recreate the backup base directory after deletion
        os.makedirs(backup_base_path)

def backup_and_update(src_folder, dest_folder, backup_folder):
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

def main():
    base_update_path = "/home/debian/update"
    backup_base_path = "/home/debian/backup"
    json_config_path = "/home/debian/Log/credentials.json"  # Path to your JSON file

    # Load JSON configuration
    config = load_json_config(json_config_path)

    # Extract version from the JSON structure
    version = config.get("server", {}).get("version", "Unknown version")
    
    print(f"Starting update process with version {version}.")

    # Delete all previous backups in the backup folder
    delete_all_backups(backup_base_path)

    # Define the versioned backup directory
    versioned_backup_path = os.path.join(backup_base_path, version)
    ensure_directory(versioned_backup_path)

    # Define the corresponding backup subfolders for each type of update
    paths = {
        "codes": {"src": os.path.join(base_update_path, "codes"), "dest": "/home/debian/codes", "backup": os.path.join(versioned_backup_path, "codes")},
        "Log": {"src": os.path.join(base_update_path, "Log"), "dest": "/home/debian/Log", "backup": os.path.join(versioned_backup_path, "Log")},
        "html": {"src": os.path.join(base_update_path, "html"), "dest": "/var/www/html", "backup": os.path.join(versioned_backup_path, "html")},
    }

    # Make sure the subfolders inside versioned backup folder exist
    for folder, paths_info in paths.items():
        backup_folder = paths_info["backup"]
        ensure_directory(backup_folder)

    # Perform the backup and update for each folder
    for folder, paths_info in paths.items():
        src = paths_info["src"]
        dest = paths_info["dest"]
        backup = paths_info["backup"]

        if os.path.exists(src):
            print(f"Updating {folder} from {src} to {dest}, with backups in {backup}.")
            backup_and_update(src, dest, backup)
        else:
            print(f"Source folder {src} does not exist. Skipping {folder}.")

    print("Update completed successfully.")

if __name__ == "__main__":
    main()
