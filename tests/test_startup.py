import os
import subprocess
import sys
from app.settings_manager import ROOT

def test_gui_startup():
    env = os.environ | {'QT_QPA_PLATFORM':'offscreen'}
    result = subprocess.run([sys.executable,str(ROOT/'main.py'),'--smoke-test'],
                            cwd=ROOT,env=env,capture_output=True,text=True,timeout=45)
    assert result.returncode == 0, result.stdout + result.stderr
