# Galaxy AOSP Experience — A35X ROM Builder

## Adopted build profile

- Device: Samsung Galaxy A35 5G, SM-A356E (a35x).
- Biometric strategy: BOTH, implemented as two separately testable paths:
  1. Stock vendor biometric HAL + original TEE/KeyMint chain preserved.
  2. Experimental AOSP compatibility path, isolated from the stock path.
- Google services: GApps selectable, never mandatory. AOSP/vanilla remains a supported output.
- Galaxy Experience: selective modules, all disabled by default until individually validated.
- Kernel: BOTH stock firmware kernel and source-built kernel.
- Filesystem: EXT4 baseline; EROFS only after device-tree, partition and OTA/package validation.

## Layered architecture

    ROM Builder / Build Orchestrator
      ├── Android source manifest (15 / 16; 17 gated until source branch exists)
      ├── Firmware catalog + binary compatibility validator
      ├── Device tree + vendor blobs
      ├── Kernel provider
      │     ├── stock: matching firmware kernel, DTB/DTBO and modules
      │     └── source: pinned repository, revision, defconfig and toolchain
      ├── Filesystem provider (EXT4 / EROFS)
      ├── GApps provider (none / supported package)
      ├── Hardware compatibility
      │     ├── biometrics stock path
      │     ├── experimental AOSP path
      │     ├── TEE / KeyMint / Gatekeeper
      │     └── camera / audio / sensors / connectivity
      ├── Galaxy Experience module installer
      │     ├── Game Launcher
      │     ├── Game Booster
      │     ├── Galaxy Avatar / AR Zone
      │     ├── Samsung Camera
      │     ├── Samsung Keyboard
      │     └── Galaxy Services (allowlisted dependencies only)
      └── Validation + artifact manifest

## Non-negotiable compatibility rules

1. Never replace or strip TEE, KeyMint, Gatekeeper, biometric vendor services, camera HALs, firmware or vendor libraries as generic debloat.
2. The stock biometric path is the reference implementation. The AOSP path is an experimental alternative, not a runtime overlay that races the stock HAL.
3. Do not claim under-display fingerprint support until enrollment, unlock, app authentication, reboot persistence and repeated enrollment/removal pass on the actual SM-A356E.
4. Each Galaxy module is optional and fail-open: missing packages, framework APIs or libraries must skip that module, not abort Android boot.
5. Samsung proprietary APKs and libraries must be extracted from firmware supplied by the user or obtained under an applicable license. Do not redistribute proprietary payloads in this repository or build artifacts.
6. Never use a package name alone as proof that a Samsung service is safe to remove. Debloat uses an explicit allowlist and dependency checks.
7. Do not disable thermal protections. Undervolt/overclock is unavailable unless the selected kernel exposes validated controls and the hardware is tested.
8. Keep the required baseline security patch 2025-04-01 for the stated test baseline; changing it requires an explicit firmware/test-baseline update.

## Build configuration contract

The canonical defaults live in config/rom-builder.defaults.json; Galaxy module metadata lives in config/galaxy-experience.modules.json.

Workflow inputs should be translated into a generated build config, validated before repo sync and before packaging. Do not interpolate free-form user input directly into shell commands. Validate enumerated values and pin external repositories to explicit revisions.

### Android source versions

Current known workflow mapping:
- Android 15 -> LineageOS lineage-22.2
- Android 16 -> LineageOS lineage-23.2

Android 17 remains experimental/disabled until a real supported manifest branch and compatible device/vendor trees are verified. GitHub Actions workflow_dispatch choice lists are static; a discovery script can validate/update the catalog, but cannot populate a dropdown dynamically during the same run.

### GApps

- none: produce a clean vanilla build.
- gapps: use a package explicitly compatible with the selected Android release, architecture and ROM install method.
- Verify release metadata, checksum/signature where published, archive layout and install scripts.
- Do not inject an arbitrary flashable ZIP by copying its system/ folder into target-files. Use a supported integration method for the selected ROM branch or produce a separately flashable GApps package.

### Kernel

- stock: use kernel, DTB/DTBO and modules matching the selected firmware binary. Verify ABI and boot image layout.
- source: require repository URL, immutable revision, defconfig, toolchain and module build outputs. Validate kernel release, symbols/ABI, DTBs, modules and boot image packaging.
- both: expose both build variants as separate jobs/artifacts; never mix stock and source kernel components in one image.

### Biometrics

- both means build/test both implementation variants independently. It does not mean loading two biometric HAL providers simultaneously.
- Preserve vendor HAL, firmware, TEE and KeyMint for the stock path.
- The AOSP compatibility path may use a shim only after its interface and trust chain are proven. No bypassing secure authentication or faking successful authentication.
- Publish a compatibility report for each build variant.

### Galaxy Experience

Each module has its own dependency list, compatibility status, install manifest and test result. The installer must:
- verify required package/API/library dependencies;
- install only selected modules;
- preserve required Samsung framework components;
- skip unsupported modules with a clear report;
- avoid mandatory boot-time services unless proven necessary;
- extract proprietary content locally from the user's firmware.

### Filesystem

EXT4 is the initial baseline. EROFS must remain unavailable until the device tree, dynamic partition sizing, AVB, target-files packaging, OTA metadata and recovery flashing path are validated. Never toggle only a workflow variable and assume the image is compatible.

## Validation gates

### Preflight
- Android source branch exists.
- Device and vendor trees are pinned and available.
- Firmware binary is catalogued and compatible with the Android/vendor baseline.
- Kernel mode has all required inputs.
- GApps package supports the Android version and install path.
- Filesystem is supported by BoardConfig, partition layout and packaging.
- Selected Galaxy modules have dependencies satisfied.

### Hardware
- Boot, reboot, recovery and encryption.
- Fingerprint enrollment, unlock, app authentication, removal and re-enrollment.
- Camera: all sensors, preview, capture, focus, flash and video.
- Audio, microphones, speakers, Wi-Fi, Bluetooth, NFC, GPS, USB and sensors.

### Release
- Generate SHA-256 checksums.
- Include build config, source revisions, firmware identifier, kernel mode, filesystem, GApps selection and module compatibility report.
- Keep debug logs and failed validation results as artifacts.
