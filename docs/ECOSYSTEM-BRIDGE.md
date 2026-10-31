# Galaxy Ecosystem Bridge

## Goal

Provide a coherent accessory experience on the A35X AOSP ROM without requiring the full One UI software stack. Support Samsung Galaxy accessories where their companion software and protocols permit it, while providing the broadest possible standard Bluetooth experience for accessories from other manufacturers.

This is an additive layer. It must not replace Android's Bluetooth stack or block normal Bluetooth pairing/audio when an optional adapter is absent.

## Device discovery and connection

- Use Android Bluetooth framework APIs and supported BLE discovery flows.
- Do not run continuous background scans by default. Scan on user request, system pairing flow or a bounded discovery window.
- Preserve Android permission, Nearby Devices, location and user-consent rules.
- Classify devices using advertised services, manufacturer data and supported profiles; do not identify a model from its marketing name alone.
- Keep vendor-specific support in independent adapters so one vendor's integration cannot break another.

## Audio and battery reporting

The unified accessory model supports:
- left earbud battery;
- right earbud battery;
- charging-case battery;
- headset/headband battery;
- aggregate battery;
- charging/full/unknown state.

Only expose a field when the accessory reports it through a standard or verified vendor protocol. Unknown values remain null/unknown. Never estimate a charging-case percentage or split an aggregate reading into left/right values.

Protocol tiers:
1. Standard Android Bluetooth profiles and device metadata for baseline pairing, calls, media and controls.
2. Bluetooth Battery Service / supported headset battery reporting for the values those devices actually expose.
3. Fast Pair when the accessory supports the relevant Fast Pair extensions and the ROM includes a compatible, licensed/authorized provider implementation. Per-earbud and case readings require explicit accessory support.
4. Optional manufacturer adapters for proprietary protocols, individually validated by model and firmware.

Not every generic headset exposes separate left/right/case percentages. This is a hardware/protocol limitation, not something the ROM can safely infer.

## Galaxy Buds

- Treat Galaxy Buds as a family of model-specific devices, not one universal protocol.
- Validate Galaxy Wearable and the matching Buds Manager/plugin against the selected Android release and firmware.
- Keep basic Bluetooth audio usable even when the companion plugin or advanced settings are unavailable.
- Expose battery, ANC/ambient, touch controls, equalizer and firmware update only where the specific model and plugin support them.
- Do not redistribute Samsung proprietary APKs or libraries. Extract from user-provided firmware/packages where legally permitted, or require the user to install the official companion package.

## Galaxy Watch and other wearables

- Keep Android Bluetooth and Wear OS companion pairing paths intact.
- Galaxy Watch generations differ: Wear OS watches and older Tizen watches need separate compatibility handling.
- Galaxy Wearable device plugins are model-specific. Some advanced features may be limited on non-One-UI devices.
- Samsung documentation states Wear OS Galaxy Watch setup requires a compatible Android phone and GMS; therefore full Watch4+ setup must be tested with the selected GApps/GMS configuration. AOSP-without-GMS cannot be advertised as providing full official Galaxy Watch setup.
- Samsung Health features and sensor SDKs have separate SDK, partner, app-signature and device restrictions. Do not promise access to ECG, blood pressure, body composition or other protected health measurements through a generic bridge.

## UI

Create one optional system settings area: **Connected ecosystem**.
- Nearby devices and connection state.
- Per-device detail page.
- Battery cards with separate component rows only when available.
- Companion app / plugin status and missing dependency explanation.
- Supported controls and firmware information.
- Disconnect, forget and permission controls.

Do not copy a proprietary UI or require a Samsung account for basic Bluetooth functionality.

## Privacy and reliability

- No continuous scanning without user consent.
- No accessory telemetry uploaded by default.
- Store only necessary local device metadata.
- Vendor adapters run with least privilege and explicit permissions.
- Adapter crashes must not crash Bluetooth services or System UI.
- Unavailable features are marked unsupported rather than shown as broken toggles.

## Validation matrix

Test at minimum:
- Galaxy Buds models available for physical testing (each generation separately).
- One Fast Pair-certified TWS model with left/right/case battery support.
- One generic TWS without Fast Pair.
- One over-ear Bluetooth headset.
- One speaker.
- Galaxy Watch Wear OS generation and, if in scope, a legacy Tizen watch.

For every device, test discovery, pairing, reconnect after reboot, media/call routing, battery accuracy, charging transitions, disconnect/forget and behavior when its companion app is absent.
