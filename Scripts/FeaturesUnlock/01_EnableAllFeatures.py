import os
import sys
import re

if len(sys.argv) < 2:
    print("Usage: python3 EnableAllFeatures.py <decompiled_dir>")
    sys.exit(1)

decompiled_dir = sys.argv[1]

# Find the ifc.smali class which handles Phenotype boolean flags
ifc_path = None
for root, dirs, files in os.walk(decompiled_dir):
    if "ifc.smali" in files:
        ifc_path = os.path.join(root, "ifc.smali")
        break

if not ifc_path:
    print("Error: ifc.smali not found. Features might already be unlocked or class name changed.")
    sys.exit(1)

with open(ifc_path, "r") as f:
    content = f.read()

# Replace the body of j()Z to always return true (const/4 v0, 0x1)
pattern = r"\.method public final j\(\)Z\s+\.locals \d+\s+(.*?)\.end method"
replacement = r""".method public final j()Z
    .locals 1

    const/4 v0, 0x1

    return v0
.end method"""

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

if content == new_content:
    print("Warning: Could not patch j()Z in ifc.smali. Maybe it's already patched?")
else:
    with open(ifc_path, "w") as f:
        f.write(new_content)
    print("Successfully forced Phenotype flags to true (Unlocked Night Mode, HDR, Lens, Aspect Ratio, etc.)")
