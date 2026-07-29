import sys, re
from pathlib import Path

root = Path(".")

constants_text = (root / "viewer" / "constants.py").read_text(encoding="utf-8")
m = re.search(r'^APP_VERSION\s*=\s*["\']([^"\']+)["\']', constants_text, re.M)
if not m:
    print("constants.py: APP_VERSION not found")
    sys.exit(1)
cv = m.group(1)

changelog_text = (root / "CHANGELOG.md").read_text(encoding="utf-8")
m = re.search(r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)", changelog_text, re.M)
if not m:
    print("CHANGELOG.md: latest version heading not found")
    sys.exit(1)
lv = m.group(1)

readme_text = (root / "README.md").read_text(encoding="utf-8")
m = re.search(r"badge/版本/([^/\)]+)", readme_text)
if not m:
    print("README.md: version badge not found")
    sys.exit(1)
rv = m.group(1)

versions = {"constants.py": cv, "CHANGELOG.md": lv, "README.md": rv}
if len(set(versions.values())) != 1:
    print("Version mismatch:")
    for k, v in versions.items():
        print(f"  {k}: {v}")
    sys.exit(1)

print("Version OK: " + cv)
