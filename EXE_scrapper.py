import os
import argparse
import shutil
import logging
import hashlib

#
# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(f"EXE_scrapper.log", mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Arguments
parser = argparse.ArgumentParser(description='Scrap EXE files from a folder')
parser.add_argument('--input-folder', type=str, help='Folder to scrap EXE files from')
parser.add_argument('--output-folder', type=str, help='Folder to save the EXE files to')


def compute_file_hash(file_path, algorithm='sha256'):
    """Compute the hash of a file using the specified algorithm."""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as file:
        # Read the file in chunks of 8192 bytes
        while chunk := file.read(8192):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

# Main
def main() -> int:
    # Parse arguments
    args = parser.parse_args()
    logger.info(f"Input folder: {args.input_folder}")
    logger.info(f"Output folder: {args.output_folder}")

    # Check if input folder exists
    if not os.path.exists(args.input_folder):
        logger.error(f"Input folder {args.input_folder} does not exist")
        return 1
    
    # Check if output folder exists and create if not
    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)
        logger.info(f"Created output folder {args.output_folder}")


    for root, dirnames, files in os.walk(args.input_folder):
        for file in files:
            if file.endswith('.exe'):
                file_path = os.path.join(root, file)
                try:
                    new_file_name = compute_file_hash(file_path)
                    shutil.copy(file_path, os.path.join(args.output_folder, new_file_name))
                    logger.info(f"Copied file from {file_path} to {args.output_folder}")
                except Exception as ex:
                    logger.error(f"Failed to copy {file_path} to {args.output_folder}")
                    logger.error(ex)

    return 0

if __name__ == '__main__':
    main()