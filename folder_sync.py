import os
import shutil
import time
import argparse
import hashlib
import logging


def create_replica_folder(replica_path):
    if not os.path.exists(replica_path):
        os.makedirs(replica_path)


def calculate_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as file:
        while True:
            data = file.read(65536)  # Read in 64k chunks
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def configure_logging(log_file):
    # Ensure the directory where the log file will be located exists; create it if it doesn't
    log_directory = os.path.dirname(log_file)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Configure the logging to use the specified log file location
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def synchronize_folders(original_path, replica_path, log_file, interval):
    create_replica_folder(replica_path)

    configure_logging(log_file)

    while True:
        for root, dirs, files in os.walk(original_path):
            for dir in dirs:
                original_dir_path = os.path.join(root, dir)
                replica_dir_path = os.path.join(replica_path, os.path.relpath(original_dir_path, original_path))
                if not os.path.exists(replica_dir_path):
                    os.makedirs(replica_dir_path)

            for file in files:
                original_file_path = os.path.join(root, file)
                replica_file_path = os.path.join(replica_path, os.path.relpath(original_file_path, original_path))

                if not os.path.exists(replica_file_path) or calculate_hash(original_file_path) != calculate_hash(replica_file_path):
                    shutil.copy2(original_file_path, replica_file_path)
                    logging.info(f"File updated: {original_file_path} to {replica_file_path}")
                    print(f"File updated: {original_file_path} to {replica_file_path}")

        # Check for files and directories in replica folder that are not in the original folder
        for root, dirs, files in os.walk(replica_path):
            for dir in dirs:
                replica_dir_path = os.path.join(root, dir)
                original_dir_path = os.path.join(original_path, os.path.relpath(replica_dir_path, replica_path))
                if not os.path.exists(original_dir_path):
                    shutil.rmtree(replica_dir_path)
                    logging.info(f"Directory removed: {replica_dir_path}")
                    print(f"Directory removed: {replica_dir_path}")

            for file in files:
                replica_file_path = os.path.join(root, file)
                original_file_path = os.path.join(original_path, os.path.relpath(replica_file_path, replica_path))
                if not os.path.exists(original_file_path):
                    os.remove(replica_file_path)
                    logging.info(f"File removed: {replica_file_path}")
                    print(f"File removed: {replica_file_path}")

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize folders")
    parser.add_argument("original_folder", help="Path to the original folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("log_file", help="Path to the log file. Log file name e.g.: log_file.log")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")

    args = parser.parse_args()
    synchronize_folders(args.original_folder, args.replica_folder, args.log_file, args.interval)
