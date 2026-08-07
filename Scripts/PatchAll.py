#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import re

if len(sys.argv) < 2:
    print("Usage: ./PatchAll.py <GcamGo.apk>")
    sys.exit(1)

input_apk = os.path.abspath(sys.argv[1])
if not os.path.isfile(input_apk) or not input_apk.endswith(".apk"):
    print("Error: Input must be an APK file.")
    sys.exit(1)

base_dir = os.path.dirname(input_apk)
input_name = os.path.basename(input_apk)
name_no_ext = os.path.splitext(input_name)[0]

script_dir = os.path.dirname(os.path.realpath(__file__))
apktool_path = os.path.join(script_dir, "..", "apktool_3.0.3.jar")
keystore_path = os.path.join(script_dir, "mod_keystore.keystore")

if not os.path.exists(apktool_path):
    print(f"Error: apktool jar not found at '{apktool_path}'")
    sys.exit(1)

decompiled_dir = os.path.join(base_dir, f"{name_no_ext}_temp_decompiled")
out_apk = os.path.join(base_dir, "GcamGo_Modified.apk")
unsigned_apk = os.path.join(base_dir, "GcamGo_unsigned.apk")

print(f"[*] Decompiling {input_name}...")
subprocess.run(["java", "-jar", apktool_path, "d", input_apk, "-f", "-o", decompiled_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

features_dir = os.path.join(script_dir, "FeaturesUnlock")

print("")
if os.path.isdir(features_dir):
    feature_scripts = sorted([f for f in os.listdir(features_dir) if f.endswith(".py")])
    for script in feature_scripts:
        name = os.path.splitext(script)[0]
        name = re.sub(r'^\d+_', '', name) 
        
        if "MinimalBooting" in name:
            pretty_name = "Minimal Booting"
        elif name.startswith("Enable"):
            suffix = name[6:]
            spaced = re.sub(r'([A-Z])', r' \1', suffix).strip()
            spaced = spaced.replace("H D R", "HDR")
            pretty_name = "Enable " + spaced
        else:
            pretty_name = name
            
        print(f"Patching For {pretty_name} ", end="", flush=True)
        
        script_path = os.path.join(features_dir, script)
        result = subprocess.run([sys.executable, script_path, decompiled_dir], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK]")
        else:
            print("[FAILED]")
            print(result.stderr)
else:
    print(f"[-] FeaturesUnlock folder not found at {features_dir}")
print("")

print("[*] Recompiling APK...")
subprocess.run(["java", "-jar", apktool_path, "b", decompiled_dir, "-o", unsigned_apk], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if not os.path.exists(keystore_path):
    print("[*] Generating new keystore...")
    subprocess.run([
        "keytool", "-genkey", "-v", "-keystore", keystore_path, "-alias", "mod", 
        "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000", 
        "-storepass", "password", "-keypass", "password", 
        "-dname", "CN=Modder, OU=Mod, O=Mod, L=Mod, S=Mod, C=US"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("[*] Signing APK...")
subprocess.run([
    "apksigner", "sign", "--ks", keystore_path, "--ks-pass", "pass:password", 
    "--out", out_apk, unsigned_apk
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("[*] Cleaning up temporary files...")
shutil.rmtree(decompiled_dir)
if os.path.exists(unsigned_apk):
    os.remove(unsigned_apk)
if os.path.exists(out_apk + ".idsig"):
    os.remove(out_apk + ".idsig")

print(f"\n[SUCCESS] Modified APK created: {out_apk}")
