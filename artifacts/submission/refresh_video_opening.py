"""Refresh only the static opening from the final public screenshot; preserve narration."""
from pathlib import Path
import json,subprocess
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/submission'
cut=json.loads((OUT/'recording-scene-times.json').read_text())[2]['start']
ff=imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff,'-y','-v','error','-i',str(OUT/'demo-narrated.webm'),'-loop','1','-framerate','25','-i',str(OUT/'project-screenshot.png'),'-filter_complex',f'[0:v][1:v]overlay=0:0:enable=lt(t\\,{cut})[v]','-map','[v]','-map','0:a:0','-c:v','libvpx-vp9','-crf','30','-b:v','0','-deadline','realtime','-cpu-used','6','-row-mt','1','-threads','4','-c:a','copy','-t','108.12',str(OUT/'demo-final.webm')],check=True)
print('FINAL_OPENING_REFRESHED')
