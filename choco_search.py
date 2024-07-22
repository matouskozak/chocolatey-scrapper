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

file_handler = logging.FileHandler(f"choco_search.log", mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

arr_packages = []
i = 0 # reset to 0 to scrap all packages

while True:
	try:
		#search_call = ["choco", "search", "--page", str(i), "--id-only", "--limit-output"]
		search_call = ["choco", "search", "--page", str(i), "--limit-output"]
		logger.info(f"{' '.join(search_call)}")

		proc = sp.run(
			search_call,
			capture_output=True,
			text=True)
		output = proc.stdout
		exit_code = proc.returncode
		if exit_code != 0:
			logger.error(f"Failed to retrieve results for: {' '.join(search_call)}")
			break
		output_rows = output.split('\n')[:-1]
		for row in output_rows:
			name, version = row.split("|")[:2]
			arr_packages.append ([name, version])

		i += 1
		# if i > 100:
		# 	break
		
	except Exception as ex:
		print(ex)
		break

logger.info(f"Num packages: {len(arr_packages)}")

with open(f"output_{i - 1}.csv", "w", newline='', encoding='utf-8') as csv_file:
	csvwriter = csv.writer(csv_file)
	csvwriter.writerow(['name', 'version'])
	csvwriter.writerows(arr_packages)
