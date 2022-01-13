from pathlib import Path


def DirectoryExists (path_to_dir):
	Path(path_to_dir).mkdir(parents=True, exist_ok=True)
	print('Path check complete')