#!/usr/bin/env python3
"""Validate the A35X ROM Builder configuration before expensive build steps."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/rom-builder.defaults.json"
MODULES = ROOT / "config/galaxy-experience.modules.json"

def fail(message: str) -> None:
    print(f"CONFIG ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)

def main() -> None:
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        catalog = json.loads(MODULES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(str(exc))

    if cfg.get("device", {}).get("codename") != "a35x":
        fail("This configuration is reserved for device a35x.")

    android = cfg.get("android", {})
    version = str(android.get("version", ""))
    if version not in android.get("supported_versions", []):
        fail(f"Android {version} is not in the verified supported_versions list.")

    gapps = cfg.get("gapps", {})
    if gapps.get("mode") not in {"none", "gapps"}:
        fail("gapps.mode must be none or gapps.")

    kernel = cfg.get("kernel", {})
    mode = kernel.get("mode")
    if mode not in {"stock", "source", "both"}:
        fail("kernel.mode must be stock, source or both.")
    source = kernel.get("source", {})
    source_variant_enabled = bool(source.get("enabled", False))
    if mode == "source" or (mode == "both" and source_variant_enabled):
        if not all(source.get(k) for k in ("repository", "revision", "defconfig")):
            fail("An enabled source-kernel variant requires repository, immutable revision and defconfig.")
    if mode == "both" and not source_variant_enabled:
        print("NOTICE: stock-kernel variant is selected for this run; source-kernel variant remains gated.")

    fs = cfg.get("filesystem", {})
    if fs.get("mode") not in fs.get("allowed", []):
        fail("Selected filesystem is not in the allowed list.")
    if fs.get("mode") == "erofs" and not fs.get("erofs_verified", False):
        fail("EROFS is blocked until device-tree and packaging support are verified.")

    bio = cfg.get("biometrics", {})
    if bio.get("mode") != "both":
        fail("Initial adopted profile requires biometrics.mode=both.")
    if bio.get("runtime_fallback") is not False:
        fail("Biometric implementations must be tested as separate variants, not raced at runtime.")

    galaxy = cfg.get("galaxy_experience", {})
    if galaxy.get("mode") != "selective":
        fail("Initial adopted profile requires selective Galaxy Experience.")
    known_modules = {m["id"] for m in catalog.get("modules", [])}
    selected = set(galaxy.get("modules", {}).keys())
    unknown = selected - known_modules
    if unknown:
        fail(f"Unknown Galaxy modules selected: {', '.join(sorted(unknown))}")

    if cfg.get("build", {}).get("preflight_required") is not True:
        fail("Preflight cannot be disabled for this project.")

    print("A35X ROM Builder configuration: valid.")
    print(f"Device: a35x | Android: {version} | GApps default: {gapps['mode']} (optional)")
    print(f"Kernel strategy: {mode} | Filesystem default: {fs['mode']} | Biometrics: isolated stock/AOSP variants")
    print("Galaxy Experience: selective (module availability is checked separately).")

if __name__ == "__main__":
    main()
