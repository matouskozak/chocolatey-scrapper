import os
import subprocess as sp
import csv
import glob
import shutil
import logging

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(f"choco_install.log", mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def extract_EXE_from_folder(source_folder, dest_folder):
	num_found = 0
	for root, dirs, files in os.walk(source_folder):
		for file in files:
			if file.endswith(".exe"): # We accept only EXE apps (no MSI, ps1, etc.)
				file_path = os.path.join(root, file)
				try:
					shutil.copy(file_path, dest_folder)
					logger.info(f"Copied file from {file_path} to {dest_folder}")
					num_found += 1
				except Exception as ex:
					logger.error(f"Failed to copy {file_path} to {dest_folder}")
					logger.error(ex)

	logger.info(f"Found {num_found} EXE files in {source_folder}")
	return num_found

# Read packages from CSV
with open("output_399.csv", "r", newline='', encoding='utf-8') as csv_file:
	csvreader = csv.reader(csv_file)
	arr_packages = list(csvreader)


# Remove header
arr_packages = arr_packages[1:]


logger.info(f"Num packages: {len(arr_packages)}")

# for package in arr_packages[:10]:
# 	name, version = package
# 	logger.info(f"Package: {name} {version}")


# Install packages, one by one
# should be run as admin
for idx, package in enumerate(arr_packages[330:]):
	idx += 330
	name, version = package
	install_call = ["choco", "install", name, "--version", version, "-y", "--allow-downgrade", "--force"]
	logger.info(f"{idx}. {' '.join(install_call)}")

	try:
		# proc = sp.run(
		# 	install_call,
		# 	capture_output=True,
		# 	text=True,
		# 	shell=True,
		# 	timeout=600)

		proc = sp.Popen(
			install_call,
			stdout=sp.PIPE,
			stderr=sp.PIPE,
			shell=True
		)
		proc.wait(600)
	except sp.TimeoutExpired as ex:
		print(ex)
		proc = None
		exit_string = "TIMEOUT"

	# Check if installation was successful
	if proc is not None:
		install_output = proc.stdout
		install_exit_code = proc.returncode

		logger.debug(f"Install output: {install_output}")

		exit_string = "SUCCESS"
		if install_exit_code != 0:
			logger.error(f"Failed to install package: {name}")
			exit_string = "ERROR"

	# Append to log file
	with open("install_log.txt", "a") as log_file:
		logger.info(f"{idx}. {name}_{version}: {exit_string}")
		log_file.write(f"{idx}. {name}_{version}: {exit_string}\n")
	
exit(0)

	# package_folder = os.path.join("scrapped_PE_files", f"{name}_{version}")
	# os.makedirs(os.path.join(package_folder), exist_ok=True)

	# # Copy installer to package folder
	# installer_package_folder = os.path.join(package_folder, "installers")
	# os.makedirs(os.path.join(installer_package_folder), exist_ok=True)

	# # Try ProgramData folder
	# name_folder = glob.glob(f"C:\\ProgramData\\chocolatey\\lib\\{name}*\\tools")
	# if len(name_folder) == 1:
	# 	extract_EXE_from_folder(name_folder[0], installer_package_folder)	
	# # Try cache folder
	# name_folder = glob.glob(f"choco_cache\\{name}*\\{version}")
	# if len(name_folder) == 1:
	# 	extract_EXE_from_folder(name_folder[0], installer_package_folder)



	# if install_exit_code != 0:
	# 	print(f"ERROR: Failed to install package: {name}")
	# 	continue
	
	# print (f"INFO: Successfully installed package: {name} {version}")
	
	# # Copy installed files from Program Files
	# program_files_package_folder = os.path.join(package_folder, "program_files")
	# os.makedirs(os.path.join(program_files_package_folder), exist_ok=True)
	# num_found = 0

	# for line in install_output.split('\n'):
	# 	if "Deployed to" in line:
	# 		print("Deployed to LINE::", line) # TODO delete
	# 		#if "Program Files" in line or "AppData" in line:
	# 		program_files_folder = re.findall("'([^']*)'", line)
	# 		assert len(program_files_folder) == 1
	# 		program_files_folder_path = program_files_folder[0]
	# 		# Remove quotes
	# 		program_files_folder_path = program_files_folder_path.replace('"', '')
	# 		print("INFO: Found installation folder:", program_files_folder_path)
	# 		extract_EXE_from_folder(program_files_folder_path, program_files_package_folder)
	# 		# for root, dirs, files in os.walk(program_files_folder_path):
	# 		# 	for file in files:
	# 		# 		if file.endswith(".exe"):
	# 		# 			shutil.copy(os.path.join(root, file), program_files_package_folder)
	# 		# 			print(f"INFO: Copied {file} to {program_files_package_folder}") # Add counter
	# 		# 			num_found += 1

	# 		# print(f"INFO: Found {num_found} EXE files in {program_files_folder_path}")


			
	# # Remove installer from cache
	# #shutil.rmtree(name_folder)

	# # Uninstall package
	# uninstall_call = ["choco", "uninstall", name, "-y", "--force"]
	# print("INFO:", " ".join(uninstall_call))
	# for _ in range(2): # Just to be sure
	# 	sp.run(
	# 		uninstall_call,
	# 		capture_output=True,
	# 		text=True)

	# print(50*"-")
