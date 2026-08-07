#!/usr/bin/env python3
import os
import sys
import subprocess

if len(sys.argv) < 2:
    print("Usage: ./SimpleExtract.py <APK_FILE>")
    sys.exit(1)

input_path = os.path.abspath(sys.argv[1])
if not os.path.exists(input_path):
    print(f"File not found: {input_path}")
    sys.exit(1)

if not input_path.endswith(".apk"):
    print("Input must be an APK file.")
    sys.exit(1)

script_dir = os.path.dirname(os.path.realpath(__file__))
apktool_path = os.path.join(script_dir, "..", "apktool_3.0.3.jar")

if not os.path.exists(apktool_path):
    print(f"Error: apktool jar not found at '{apktool_path}'")
    sys.exit(1)

input_name = os.path.basename(input_path)
name_no_ext = os.path.splitext(input_name)[0]
base_dir = os.path.dirname(input_path)
decompiled_dir = os.path.join(base_dir, f"{name_no_ext}_decompiled")

print(f"[*] Decompiling {input_name}...")
try:
    subprocess.run(["java", "-jar", apktool_path, "d", input_path, "-f", "-o", decompiled_dir], check=True)
    print(f"\n[SUCCESS] Extraction completed: {decompiled_dir}")
except subprocess.CalledProcessError as e:
    print(f"\n[ERROR] apktool exited with code {e.returncode}")
    sys.exit(e.returncode)
except FileNotFoundError:
    print("\n[ERROR] 'java' command not found. Please ensure Java is installed.")
    sys.exit(1)
