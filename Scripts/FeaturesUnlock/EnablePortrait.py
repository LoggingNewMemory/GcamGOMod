#!/usr/bin/env python3
import os
import sys
import re

def patch_feature(decompiled_dir):
    print("[*] Applying Portrait patches...")
    patched_count = 0
    
    for root, dirs, files in os.walk(decompiled_dir):
        for file in files:
            if file.endswith(".smali"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                
                modified = False
                
                # ==========================================
                # Add your Portrait smali regex patches here
                # ==========================================
                
                # Example: Bypass a specific Portrait check (Update with actual strings/regex)
                # if "isHdrSupported" in content:
                #     content = re.sub(r'(invoke-virtual \{[vp][0-9]+\}, L.*->isHdrSupported\(\)Z\s+)move-result ([vp][0-9]+)', 
                #                      r'\g<1>const/4 \2, 0x1', content)
                #     print(f"  [+] Forced Portrait support in {file}")
                #     modified = True
                
                if modified:
                    with open(filepath, "w") as f:
                        f.write(content)
                    patched_count += 1

    if patched_count == 0:
        print("  [-] No files were patched. Please add the exact Portrait regex to EnablePortrait.py.")
    else:
        print(f"\n[SUCCESS] Portrait patch applied to {patched_count} files.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./EnablePortrait.py <GcamGo_decompiled_folder>")
        sys.exit(1)

    decompiled_dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(decompiled_dir):
        print(f"Error: Directory not found: {decompiled_dir}")
        sys.exit(1)
        
    patch_feature(decompiled_dir)
