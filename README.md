# Khmer AI Virtual Try-On

A Windows desktop smart mirror built with Python 3.11, PySide6, OpenCV and **MediaPipe Tasks**. All camera inference is local. The clothing renderer is a landmark-aligned **2D PNG overlay**, not generative try-on or physically accurate cloth simulation.

## Install and start on Windows 10/11

1. Install 64-bit Python **3.11** from https://www.python.org/downloads/release/python-3119/ with the Python launcher enabled. The workspace-local Python installed during development also works.
2. Double-click `setup.bat`. Internet access is required once for dependencies, official model bundles, and the Khmer font. Setup preserves existing catalog and garment files.
3. Double-click `start.bat`. Allow desktop apps to access the camera in Windows Privacy settings.
4. Stand roughly 2–3 metres from the camera, facing it, with even lighting and your feet in view. Adjust distance to the camera's field of view.
5. Press **F11** for full-screen exhibition mode. Escape exits full screen; another Escape returns to welcome. Close the window to quit.

Manual setup in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m utils.generate_assets
.\.venv\Scripts\python.exe -m utils.download_models
.\.venv\Scripts\python.exe main.py
```

The dependency set uses MediaPipe 0.10.21 and its current Tasks API, with NumPy 1.26 and OpenCV 4.11 for compatibility. Do not replace this environment with Python 3.14 or mix different OpenCV distributions. After successful setup, no network connection is needed. The app does not start a web server or upload images.

## Visitor experience

The welcome animation transitions to the mirror after a reliable body detection persists for 0.6 seconds. It returns after 20 seconds without a detected visitor. A start button is also available. Seven illustrative collections include men's, women's, wedding, sampot, ceremonial, Apsara-inspired and modern designs. Filter by collection or fit and select a thumbnail.

| Action | Gesture | Fallback |
| --- | --- | --- |
| Next / previous outfit | Open hand swipes across the screen | Right / Left arrows, buttons |
| Open collection | Open palm held for 0.65 seconds | Collection button |
| Selection mode | Open hand held high for 1.8 seconds | Click a thumbnail |
| Take photo | Upright thumbs-up held for 0.8 seconds | Space or Take photo |

Gestures use one hand, normalized travel thresholds, hold timing and a one-second cooldown. Selection mode reveals and focuses the carousel; swipe to change the active selection. Release your hand between repeated poses. Swipes follow **screen direction**, including when mirror mode is off. Gesture recognition is heuristic and needs calibration with real visitors, hand orientations, and lighting; it is not sign-language recognition.

Photo capture counts down from three and cancels if tracking is lost. Preview, retake, Save, and Export are available. Save writes a unique PNG into the configured folder; Export opens a file chooser for another destination. Unsaved photos exist only in memory, and previews close after visitor absence. Saved photos remain until the exhibition operator deletes them. No biometric identity records or session database are created. Optional QR sharing is **not enabled or implemented**: no misleading, unreachable QR links are displayed.

## Settings and performance

Settings control camera index, capture resolution, mirroring, English/Khmer, confidence, garment scale, output folder, inference width, hand inference frequency, full screen, and photo frame. Applying settings restarts the worker safely. The app does not enumerate devices: try camera indices 0, 1, or 2.

Capture defaults to 1280×720; pose inference uses a 640-pixel-wide frame, with hand inference every third frame. A background QThread owns camera access and inference. The GUI polls a single latest-frame slot instead of accumulating stale queued images. Garments are cached, landmarks are smoothed, and compositing uses premultiplied alpha restricted to each garment's bounding region. CPU is the default; no GPU is required. **24–30 FPS is a target, not a measured guarantee.** Reduce inference width to 384/512 or use 640×480 capture on slower machines. Large PNGs also affect performance.

The renderer uses shoulder/hip anchors for tops and hip/ankle anchors for bottoms. Low-confidence body regions are hidden immediately; tracking reacquires without carrying stale landmarks into a new visitor. Basic forearm masking restores narrow strips from the camera image. It is an approximation, not segmentation or depth-aware occlusion. Use a frontal stance; profile poses, crossed arms, fast movement, loose garments, and multiple overlapping people can produce artifacts. Only one visitor is tracked.

## Replace placeholder garments

All included artwork is original **geometric demonstration artwork**, not authentic costume photography or a claim of culturally accurate traditional dress. Before a public fashion exhibition, replace it with licensed, culturally reviewed transparent garment cutouts. Do not use the demonstration assets as authoritative references for Khmer clothing.

`assets/clothes/catalog.json` contains a list of outfits:

```json
{
  "id": "unique-id",
  "name": "Display name",
  "name_km": "ឈ្មោះ",
  "category": "Wedding",
  "gender": "unisex",
  "placeholder": true,
  "thumbnail": "traditional/preview.png",
  "layers": [
    {
      "kind": "upper",
      "asset": "traditional/top.png",
      "anchors": [[0.225, 0.125], [0.775, 0.125], [0.5, 0.83]],
      "scale": 1.0
    }
  ]
}
```

Assets must be RGBA PNGs inside the clothes directory. Coordinates are normalized to image width/height. The three upper-layer anchors are **screen-left shoulder, screen-right shoulder, hip midpoint**. Lower-layer anchors are **screen-left hip, screen-right hip, ankle midpoint**. Anchors must not be collinear. Design PNG margins around the body anchors, not around the image border. Add upper/lower layers in drawing order, with unique outfit IDs and a thumbnail. Gender accepts `male`, `female`, or `unisex`. Restart the application after edits. The asset generator never overwrites existing PNGs or a catalog. The footer intentionally labels the bundled collection as placeholders; update that wording only after replacing and reviewing every asset.

## Khmer typography

Setup downloads Noto Sans Khmer and its SIL Open Font License to `assets/fonts/`. Qt loads it before building widgets. Windows Leelawadee UI is the fallback. The interface includes Khmer labels, instructions, collection categories, and outfit names; operator diagnostic messages remain English. Have a native Khmer speaker review language and cultural presentation before public use.

## Models and documentation

Official sources used by `utils/download_models.py`:

- Pose Lite: https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task
- Hand Landmarker: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
- Pose Tasks API: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker/python
- Hand Tasks API: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python
- Font and license: https://github.com/google/fonts/tree/main/ofl/notosanskhmer

Downloaded model bundles are checked as ZIP containers and a SHA-256 provenance manifest is written to `models/download_manifest.json`. The manifest records downloaded bytes; it is not an independently verified upstream checksum. The runtime makes no model download requests.

## Testing

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe main.py --smoke-test --screenshot
.\.venv\Scripts\python.exe -m utils.check_hardware
.\.venv\Scripts\python.exe -m utils.check_pipeline
```

Tests cover affine geometry, transparent/opaque compositing, configuration validation and persistence, metadata/path validation, layered rendering with visibility gating, gesture timing/cooldown, explicit photo saving, and GUI startup. The smoke test uses no mock camera and performs no camera acquisition; it is a separate no-hardware startup mode. Its screenshot is stored in `screenshots/welcome.png`.

The hardware diagnostic initializes both actual models, runs blank-frame inference, and attempts 30 real webcam frames. It writes `hardware_report.json` containing counts and dimensions only; it does not save webcam images. A camera driver that blocks can also block this diagnostic.

The pipeline diagnostic runs the actual camera worker for 12 seconds and writes `pipeline_report.json`, without saving frames. See `TEST_REPORT.md` for the measured results and outstanding field checks. `requirements-lock.txt` records the installed environment for reproduction; `requirements.txt` remains the normal setup entry point.

Before an exhibition, test with the **actual webcam and venue lighting**: different visitor heights, all gesture controls, left/right mirroring, camera unplug/reconnect, photo cancellation on visitor departure, save folder permissions, Khmer font rendering, settings changes, full-screen return, idle reset, and a 30-minute thermal/performance run. Automated tests cannot certify tracking quality, camera compatibility, frame rate, or cultural authenticity.

## Troubleshooting

- **Camera unavailable:** close Teams/Zoom/Camera apps, check the privacy switch and Windows desktop-camera permission, and change the camera index. The worker retries disconnected cameras every two seconds. Some webcam drivers can block during capture; avoid unplugging unstable USB devices during a live session.
- **Missing or corrupted model:** run `setup.bat`. To replace a corrupted file, delete that individual `.task` file and rerun setup. Missing tracking assets leave the live camera usable with an operator error, but disable the corresponding AI functions.
- **No clothes:** step back to expose shoulders and hips, improve lighting, face the lens, and reduce the confidence setting moderately. Bottom garments require visible ankles.
- **Jitter or lag:** improve lighting, reduce inference width/resolution, increase the hand inference interval, and avoid backlight. Placement is only a 2D approximation.
- **Khmer boxes:** rerun the font downloader and restart. Confirm the Noto Sans Khmer file exists.
- **Startup error:** inspect `app.log`, verify `catalog.json` and PNG alpha channels, and run tests. Invalid settings are reported rather than silently discarded; rename `config.json` to restore defaults.
- **Save error:** select a writable folder in Settings. Saving is local and can be slow on a network drive; use a local disk at the exhibition.

## Layout

`app/` owns tracking, gestures, geometry, camera lifecycle, assets, settings and photo handling. `ui/` owns Qt views, localization and styling. `utils/` contains repeatable setup tools. `tests/` contains non-hardware verification. `assets/`, `models/`, `screenshots/`, and the runtime-created `photos/` hold their respective data.
