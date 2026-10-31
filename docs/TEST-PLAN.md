# A35X first ROM test

## Selected first-run profile

- Device: Samsung Galaxy A35 5G, SM-A356E (a35x)
- Firmware baseline: A356EXXU4BYDC
- Vendor security patch: 2025-04-01 (enforced in the temporary build workspace)
- Android: 15 / LineageOS lineage-22.2
- Build: vanilla (no GApps), EXT4, stock firmware kernel
- Galaxy Experience modules: disabled for the first bootable baseline
- Biometrics: preserve the stock Samsung vendor HAL, TEE and KeyMint

## Current hard blocker

The device tree currently sets TARGET_FORCE_PREBUILT_KERNEL := true and points to:

device/samsung/a35x/prebuilts/kernel

The repository's prebuilts/ directory currently contains dtb.img and dtbo.img, but no kernel image. The first-run workflow therefore performs a lightweight preflight and stops before syncing the full Android source if the matching stock kernel image is absent.

Required to unlock the compile job:
1. Extract the kernel Image from the exact baseline firmware A356EXXU4BYDC (or provide a verified kernel build with matching DTB/DTBO and modules).
2. Add it to the device tree at prebuilts/kernel and verify its provenance/hash.
3. Re-run A35X Test — Android 15 (safe baseline) from the Actions tab.

Do not substitute a kernel from another firmware build. Do not enable EROFS, Android 16/17, GApps injection, or source-kernel mode until their separate compatibility checks pass.

## Test stages after the kernel gate passes

1. Repo sync and device/vendor tree integration.
2. Verify product lunch target and vendor makefiles.
3. Build vanilla EXT4 ROM with the stock kernel.
4. Publish ROM images, SHA-256 checksums and build manifest as a 14-day artifact.
5. Flash only after manual review; test first boot, recovery, encryption, fingerprint, camera, audio, radio, Wi-Fi, Bluetooth, NFC, sensors and USB.
