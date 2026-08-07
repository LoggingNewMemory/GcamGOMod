#!/usr/bin/env python3
import os
import sys
import re

def patch_feature(decompiled_dir):
    patched_count = 0
    for root, dirs, files in os.walk(decompiled_dir):
        for file in files:
            if file.endswith(".smali"):
                filepath = os.path.join(root, file)
                with open(filepath, "r") as f:
                    content = f.read()
                
                modified = False
                
                if ".field static synthetic $desugar$clinit:I" in content:
                    content = re.sub(r'\.field static synthetic \$desugar\$clinit:I', r'.field public static final synthetic $desugar$clinit:I', content)
                    modified = True
                    
                if "Invalid or Unknown INFO_SUPPORTED_HARDWARE_LEVEL:" in content:
                    content = re.sub(r'(:pswitch_2\s+const/4 [vp][0-9]+, )0x3', r'\g<1>0x2', content)
                    modified = True
                    
                if " already has a mapping for key " in content:
                    content = re.sub(r'(invoke-interface \{.*?\}, Ljava/util/Map;->containsKey\(Ljava/lang/Object;\)Z\s+move-result ([vp][0-9]+)\s+)if-nez \2, (:cond_[a-f0-9]+)', r'\g<1># if-nez \2, \3', content)
                    modified = True
                    
                if "Landroid/app/ActivityManager;->isLowRamDevice()Z" in content:
                    content = re.sub(r'(invoke-virtual \{[vp][0-9]+\}, Landroid/app/ActivityManager;->isLowRamDevice\(\)Z\s+)move-result ([vp][0-9]+)', r'\g<1>const/4 \2, 0x1', content)
                    modified = True

                if modified:
                    with open(filepath, "w") as f:
                        f.write(content)
                    patched_count += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    patch_feature(sys.argv[1])
