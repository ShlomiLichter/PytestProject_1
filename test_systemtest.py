from packaging import version
import pytest
import subprocess
import os
import shutil
from NotePad import get_notepadpp_version_info, download
from pathlib import Path

vin_original_path = os.path.join(os.getcwd(), "vin_original.txt")
vin_path = os.path.join(os.getcwd(), "vin.txt")
vin_hex = os.path.join(os.getcwd(), "vin_hex.txt")

@pytest.fixture
def checkNotepad():
   return get_notepadpp_version_info()
    
def test_check_Notpad_version(checkNotepad):
    print(checkNotepad)

def test_install_Notpad():
    info = get_notepadpp_version_info()
    if info["needs_download"]:
        out_path = Path("npp_download.exe")
        download(info["latest_url"], out_path)
        subprocess.run([str(out_path), "/S"], check=True)
        assert out_path.exists()

def test_versionComperision():
    info = get_notepadpp_version_info()
    assert info["latest_version"] == info ["installed_version"]

    

def test_vin_file_exist():
    assert  os.path.exists(vin_path)

def test_vin_17():  # check 17 charachters
    with open(vin_path, "r", encoding="utf-8") as f:
        first_line = f.readline().rstrip("\n")
        assert len(first_line) == 17

def test_vin_ASCII():  # check all ASCII numbers
    with open(vin_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert all(ord(c) < 128 for c in content)

def test_copy_vin_to_vin_original():  # copy to vin_original and validate 
    shutil.copy("vin.txt","vin_original.txt")
    assert os.path.exists(vin_original_path)

def test_convert_ASCII_to_HEX():  # convert ASCII to HEX
    with open(vin_original_path, "r", encoding="utf-8") as f:
        content = f.read()
    hex_values = [format(ord(c), "02x") for c in content]
    hex_string = " ".join(hex_values)
    with open("vin_hex.txt", "w", encoding="utf-8") as out_f:
        out_f.write(hex_string)
    assert os.path.exists(vin_hex)











