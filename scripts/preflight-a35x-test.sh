#!/usr/bin/env bash
set -Eeuo pipefail

TREE_DIR="${1:?Usage: preflight-a35x-test.sh DEVICE_TREE_DIR [REPORT_FILE]}"
REPORT="${2:-a35x-preflight-report.txt}"
BOARD_CONFIG="$TREE_DIR/BoardConfig.mk"
PREBUILT_DIR="$TREE_DIR/prebuilts"

exec > >(tee "$REPORT") 2>&1

echo "A35X TEST PREFLIGHT"
echo "Device tree: $TREE_DIR"
echo "Expected firmware baseline: A356EXXU4BYDC"
echo "Required vendor security patch: 2025-04-01"
echo

[[ -s "$BOARD_CONFIG" ]] || { echo "BLOCKED: BoardConfig.mk is missing."; exit 10; }
[[ -s "$PREBUILT_DIR/dtb.img" ]] || { echo "BLOCKED: prebuilts/dtb.img is missing."; exit 11; }
[[ -s "$PREBUILT_DIR/dtbo.img" ]] || { echo "BLOCKED: prebuilts/dtbo.img is missing."; exit 12; }

if grep -q '^TARGET_FORCE_PREBUILT_KERNEL := true$' "$BOARD_CONFIG"; then
    if [[ ! -s "$PREBUILT_DIR/kernel" ]]; then
        echo "BLOCKED: BoardConfig.mk forces a prebuilt kernel at device/samsung/a35x/prebuilts/kernel,"
        echo "but that file is absent from the current device-tree repository."
        echo "The checked-in prebuilts directory contains DTB/DTBO only; a matching boot kernel Image"
        echo "from firmware A356EXXU4BYDC (or a fully validated source-kernel variant) is required."
        exit 20
    fi
else
    echo "BLOCKED: the current BoardConfig kernel mode differs from the expected stock-prebuilt path."
    echo "Review the kernel source, defconfig, toolchain and boot-image packaging before building."
    exit 21
fi

PATCH_LINE="$(grep -E '^VENDOR_SECURITY_PATCH := ' "$BOARD_CONFIG" || true)"
if [[ "$PATCH_LINE" != "VENDOR_SECURITY_PATCH := 2025-04-01" && "$PATCH_LINE" != "VENDOR_SECURITY_PATCH := 2024-09-01" ]]; then
    echo "BLOCKED: unexpected VENDOR_SECURITY_PATCH value: ${PATCH_LINE:-<missing>}"
    echo "Refusing to overwrite an unknown baseline."
    exit 22
fi

echo "PASS: device tree has DTB, DTBO and the required prebuilt kernel."
echo "PASS: security patch value is known and can be normalized to 2025-04-01 in the build workspace."
echo "Preflight passed. The build workflow may continue."
