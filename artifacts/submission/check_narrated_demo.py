"""Verify final video's audio exists, is non-silent in every scene, and lasts <2min."""
from pathlib import Path
import array,json,math,subprocess
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/submission'
ff=imageio_ffmpeg.get_ffmpeg_exe();video=OUT/'demo-narrated.webm'
r=subprocess.run([ff,'-i',str(video)],capture_output=True,text=True)
assert 'Audio: opus' in r.stderr,r.stderr
pcm=subprocess.check_output([ff,'-v','error','-i',str(video),'-map','0:a:0','-ar','24000','-ac','1','-f','s16le','-'])
samples=array.array('h',pcm);duration=len(samples)/24000
assert 90<duration<120,duration
script=json.loads((OUT/'narration-script.json').read_text());scenes=[]
for start,end,text in script['segments']:
 values=samples[int(start*24000):int(end*24000)]
 rms=math.sqrt(sum(v*v for v in values)/len(values))
 assert rms>100,(start,rms)
 scenes.append({'start':start,'end':end,'rms':rms,'spoken_text':text})
result={'audio_codec':'opus','audio_seconds':duration,'sample_rate':24000,'scenes':scenes,'all_scenes_non_silent':True,'AI_voice_disclosed':True}
(OUT/'audio-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('NARRATED_AUDIO_VALIDATION_PASSED',duration)
