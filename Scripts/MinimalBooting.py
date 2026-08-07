#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import shutil

if len(sys.argv) < 2:
    print("Usage: ./MinimalBooting.py <GcamGo.apk | GcamGo_decompiled_folder>")
    sys.exit(1)

input_path = os.path.abspath(sys.argv[1])
if not os.path.exists(input_path):
    print(f"File or directory not found: {input_path}")
    sys.exit(1)

script_dir = os.path.dirname(os.path.realpath(__file__))
apktool_path = os.path.join(script_dir, "..", "apktool_3.0.2.jar")
keystore_path = os.path.join(script_dir, "mod_keystore.keystore")

is_apk = os.path.isfile(input_path) and input_path.endswith(".apk")
is_dir = os.path.isdir(input_path)

if not is_apk and not is_dir:
    print("Input must be an APK file or a decompiled directory.")
    sys.exit(1)

input_name = os.path.basename(input_path)
name_no_ext = os.path.splitext(input_name)[0]
base_dir = os.path.dirname(input_path)

if is_apk:
    decompiled_dir = os.path.join(base_dir, f"{name_no_ext}_temp_decompiled")
    out_apk = os.path.join(base_dir, f"{name_no_ext}_MinimalBooting.apk")
    unsigned_apk = os.path.join(base_dir, f"{name_no_ext}_unsigned.apk")
    
    print(f"[*] Decompiling {input_name}...")
    subprocess.run(["java", "-jar", apktool_path, "d", input_path, "-f", "-o", decompiled_dir], check=True)
else:
    decompiled_dir = input_path
    # If the folder name ends with '_decompiled', strip it for the output apk name
    clean_name = input_name.replace("_decompiled", "")
    out_apk = os.path.join(base_dir, f"{clean_name}_MinimalBooting.apk")
    unsigned_apk = os.path.join(base_dir, f"{clean_name}_unsigned.apk")

print("[*] Applying patches...")
for root, dirs, files in os.walk(decompiled_dir):
    for file in files:
        if file.endswith(".smali"):
            filepath = os.path.join(root, file)
            with open(filepath, "r") as f:
                content = f.read()
            
            modified = False
            
            # 1. Dalvik Verification Fix ($desugar$clinit)
            if ".field static synthetic $desugar$clinit:I" in content:
                content = re.sub(r'\.field static synthetic \$desugar\$clinit:I', r'.field public static final synthetic $desugar$clinit:I', content)
                print(f"  [+] Fixed Dalvik verification in {file}")
                modified = True
                
            # 2. Hardware Level Bypass (LEGACY -> LIMITED)
            if "Invalid or Unknown INFO_SUPPORTED_HARDWARE_LEVEL:" in content:
                content = re.sub(r'(:pswitch_2\s+const/4 [vp][0-9]+, )0x3', r'\g<1>0x2', content)
                print(f"  [+] Bypassed Hardware Level check in {file}")
                modified = True
                
            # 3. Aux Lens duplicate key Exception Bypass
            if " already has a mapping for key " in content:
                content = re.sub(r'(invoke-interface \{.*?\}, Ljava/util/Map;->containsKey\(Ljava/lang/Object;\)Z\s+move-result ([vp][0-9]+)\s+)if-nez \2, (:cond_[a-f0-9]+)', r'\g<1># if-nez \2, \3', content)
                print(f"  [+] Bypassed Aux Lens mapping exception in {file}")
                modified = True
                
            # 4. Force isLowRamDevice to true (Go Mode)
            if "Landroid/app/ActivityManager;->isLowRamDevice()Z" in content:
                content = re.sub(r'(invoke-virtual \{[vp][0-9]+\}, Landroid/app/ActivityManager;->isLowRamDevice\(\)Z\s+)move-result ([vp][0-9]+)', r'\g<1>const/4 \2, 0x1', content)
                print(f"  [+] Forced isLowRamDevice to true in {file}")
                modified = True

            if modified:
                with open(filepath, "w") as f:
                    f.write(content)

print("[*] Recompiling APK...")
subprocess.run(["java", "-jar", apktool_path, "b", decompiled_dir, "-o", unsigned_apk], check=True)

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
if is_apk:
    shutil.rmtree(decompiled_dir)
os.remove(unsigned_apk)

# Clean up .idsig files created by apksigner
idsig_file = f"{out_apk}.idsig"
if os.path.exists(idsig_file):
    os.remove(idsig_file)

print(f"\n[SUCCESS] Minimal booting mod created: {out_apk}")
