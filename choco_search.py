import os
import subprocess as sp
import csv
import glob
import shutil
import re


def extract_EXE_from_folder(source_folder, dest_folder):
	num_found = 0
	for root, dirs, files in os.walk(source_folder):
		for file in files:
			if file.endswith(".exe"): # We accept only EXE apps (no MSI, ps1, etc.)
				file_path = os.path.join(source_folder, file)
				try:
					shutil.copy(file_path, dest_folder)
					print(f"INFO: Copied file from {file_path} to {dest_folder}")
					num_found += 1
				except Exception as ex:
					print(f"ERROR: Failed to copy {file_path} to {dest_folder}")
					print(ex)

	print(f"INFO: Found {num_found} EXE files in {source_folder}")
	return num_found


arr_packages = []
i = 1 # reset to 0 to scrap all packages

while True:
	try:
		#search_call = ["choco", "search", "--page", str(i), "--id-only", "--limit-output"]
		search_call = ["choco", "search", "--page", str(i), "--limit-output"]
		print(" ".join(search_call))
		proc = sp.run(
			search_call,
			capture_output=True,
			text=True)
		output = proc.stdout
		exit_code = proc.returncode
		if exit_code != 0:
			print(f"Failed to retrieve results for: {search_call}")
			break
		output_rows = output.split('\n')[:-1]
		for row in output_rows:
			name, version = row.split("|")[:2]
			arr_packages.append ([name, version])

		i += 1
		if i > 0:
			break
	except Exception as ex:
		print(ex)
		break

#print(arr_packages)
print("Num packages:", len(arr_packages))

with open("output.txt", "w") as txt_file:
	for line in arr_packages:
		txt_file.write(",".join(line) + "\n")

with open("output.csv", "w", newline='', encoding='utf-8') as csv_file:
	csvwriter = csv.writer(csv_file)
	csvwriter.writerow(['name', 'version'])
	csvwriter.writerows(arr_packages)

# Install packages, one by one
# should be run as admin
for package in arr_packages:
	print(package)
	name, version = package
	install_call = ["choco", "install", name, "--version", version, "-y", "--allow-downgrade", "--force"]
	print("INFO:", " ".join(install_call)) # TODO better logging

	proc = sp.run(
		install_call,
		capture_output=True,
		text=True)
	install_output = proc.stdout
	install_exit_code = proc.returncode

	print(install_output)
	
	package_folder = os.path.join("scrapped_PE_files", f"{name}_{version}")
	os.makedirs(os.path.join(package_folder), exist_ok=True)

	# Copy installer to package folder
	installer_package_folder = os.path.join(package_folder, "installers")
	os.makedirs(os.path.join(installer_package_folder), exist_ok=True)

	# Try ProgramData folder
	name_folder = glob.glob(f"C:\\ProgramData\\chocolatey\\lib\\{name}*\\tools")
	if len(name_folder) == 1:
		extract_EXE_from_folder(name_folder[0], installer_package_folder)	
	# Try cache folder
	name_folder = glob.glob(f"choco_cache\\{name}*\\{version}")
	if len(name_folder) == 1:
		extract_EXE_from_folder(name_folder[0], installer_package_folder)



	if install_exit_code != 0:
		print(f"ERROR: Failed to install package: {name}")
		continue
	
	print (f"INFO: Successfully installed package: {name} {version}")
	
	# Copy installed files from Program Files
	program_files_package_folder = os.path.join(package_folder, "program_files")
	os.makedirs(os.path.join(program_files_package_folder), exist_ok=True)
	num_found = 0

	for line in install_output.split('\n'):
		if "Deployed to" in line:
			print("Deployed to LINE::", line) # TODO delete
			#if "Program Files" in line or "AppData" in line:
			program_files_folder = re.findall("'([^']*)'", line)
			assert len(program_files_folder) == 1
			program_files_folder_path = program_files_folder[0]
			# Remove quotes
			program_files_folder_path = program_files_folder_path.replace('"', '')
			print("INFO: Found installation folder:", program_files_folder_path)
			extract_EXE_from_folder(program_files_folder_path, program_files_package_folder)
			# for root, dirs, files in os.walk(program_files_folder_path):
			# 	for file in files:
			# 		if file.endswith(".exe"):
			# 			shutil.copy(os.path.join(root, file), program_files_package_folder)
			# 			print(f"INFO: Copied {file} to {program_files_package_folder}") # Add counter
			# 			num_found += 1

			# print(f"INFO: Found {num_found} EXE files in {program_files_folder_path}")


			
	# Remove installer from cache
	#shutil.rmtree(name_folder)

	# Uninstall package
	uninstall_call = ["choco", "uninstall", name, "-y", "--force"]
	print("INFO:", " ".join(uninstall_call))
	for _ in range(2): # Just to be sure
		sp.run(
			uninstall_call,
			capture_output=True,
			text=True)

	print(50*"-")
