"""Download official Google MediaPipe Tasks bundles and a licensed Khmer font."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = {
 'models/pose_landmarker_lite.task': 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
 'models/hand_landmarker.task': 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
 'assets/fonts/NotoSansKhmer.ttf': 'https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskhmer/NotoSansKhmer%5Bwdth,wght%5D.ttf',
 'assets/fonts/OFL.txt': 'https://raw.githubusercontent.com/google/fonts/main/ofl/notosanskhmer/OFL.txt'
}

def download():
    records = {}
    for relative, url in DOWNLOADS.items():
        target = ROOT/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            print(f'Downloading {relative} ...', flush=True)
            temporary = target.with_suffix('.download')
            try:
                with urllib.request.urlopen(url, timeout=90) as response, temporary.open('wb') as output:
                    while chunk := response.read(1024*1024):
                        output.write(chunk)
                if target.suffix == '.task' and not zipfile.is_zipfile(temporary):
                    raise ValueError(f'Invalid model bundle: {relative}')
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)
        records[relative] = dict(url=url, sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    (ROOT/'models/download_manifest.json').write_text(json.dumps(records,indent=2),'utf-8')
    print('Models and Khmer font ready.')

if __name__ == '__main__':
    download()
