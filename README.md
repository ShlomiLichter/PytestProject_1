# PytestProject_1

## Overview
This project demonstrates automated testing and utility functions using Python and pytest. It includes:
- Downloading and installing Notepad++ silently
- Checking file properties (existence, ASCII content, line length)
- Converting file contents from ASCII to hexadecimal
- Copying and manipulating text files

## Features
- **Notepad++ Version Check & Download:**
  - Detects installed Notepad++ version
  - Downloads the latest installer if needed
  - Supports silent installation
- **File Utilities:**
  - Check if a file exists
  - Verify if all characters in a file are ASCII
  - Check if the first line of a file has 17 characters
  - Convert file contents to hexadecimal and save to a new file
  - Copy files to new names

## Testing
All main features are covered by tests in `test_systemtest.py` using pytest fixtures and functions. Example tests:
- Validate Notepad++ version and download logic
- File existence and content checks
- ASCII and hex conversion

## Usage
1. **Install dependencies:**
	```sh
	pip install pytest requests packaging
	```
2. **Run tests:**
	```sh
	pytest
	```
3. **Run Notepad++ installer logic:**
	- Execute `NotePad.py` directly or use the provided functions in your own scripts.

## Project Structure
- `NotePad.py` — Main logic for Notepad++ version detection, download, and file utilities
- `test_systemtest.py` — Pytest-based tests for all features
- `README.md` — Project documentation

## Requirements
- Python 3.10+
- Windows OS (for Notepad++ installer logic)
- Notepad++ (optional, for file opening)

## License
MIT License

---
Feel free to extend the project with more file utilities or tests as needed.
