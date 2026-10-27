# Validation — 26 October 2026

## Environment

- Windows; workspace-local Python 3.11.9 and project `.venv`.
- MediaPipe 0.10.21, OpenCV 4.11.0, NumPy 1.26.4, PySide6 6.9.3, Pillow 11.3.0.
- `pip check`: no broken requirements.
- Official Pose Lite and Hand Landmarker models downloaded, opened, and exercised with blank-frame inference.
- Noto Sans Khmer downloaded with its SIL Open Font License.

## Automated and visual checks

- **17 automated tests passed**: geometry, compositing, clipping, settings, catalog validation, layered rendering, explicit photo saving, gesture filtering, capture cancellation, idle reset, and GUI startup.
- English and Khmer startup windows rendered and inspected. Screenshots are in `screenshots/`.
- Corrected selected-card text contrast after inspecting the English screenshot.
- Python compilation passed before runtime testing.

## Actual hardware checks

- Camera index 0 opened and delivered 30 real frames.
- Requested 1280×720; actual camera output was **640×480**.
- The combined threaded pipeline delivered **63 frames during a 12-second test including initialization**, with **no reported pipeline errors**.
- Median worker-reported FPS after initial samples: **8.17 FPS**. This is below the 24–30 FPS target. It is an observation of this machine/session, not a performance guarantee or a full-body rendering benchmark.
- **No person or full body was detected** in that test. Clothing placement on a real visitor, live gestures, and visitor photo capture therefore remain unverified. Synthetic geometry/gesture tests are not substitutes for these checks.
- No camera images or visitor photos were saved during diagnostics.
- Camera capture and model resources were released at the end of the diagnostics.

See `hardware_report.json` and `pipeline_report.json` for machine-readable results. Run the manual exhibition checks in README.md with the actual visitor position and venue lighting before public deployment. Disconnect/reconnect behavior is implemented but has not been physically tested by unplugging the camera. Long-duration stability, photographic clothing authenticity, and native-language review remain field acceptance tasks.

## Scope limits

The included garments are explicitly labeled geometric placeholders. The app renders 2D overlays with approximate forearm masking, not realistic AI-generated cloth. QR sharing, a hosted download service, and optional SQLite session metadata are not implemented. Photos remain local and are saved only through an explicit Save or Export action.
