"""Add cached AI narration to the final captured walkthrough; never touch forecasts."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,wave
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from environment import load_environment
load_environment()
import imageio_ffmpeg
from openai import OpenAI
OUT=ROOT/'artifacts/submission';CACHE=OUT/'narration';CACHE.mkdir(exist_ok=True)
FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
TEXTS=[
'Four point three two three percent less historical forecast error than Pacific. The gain is uncertain. GPU Value Scientist shows the evidence. This voice is AI generated.',
'One H one hundred record stayed at ninety-four cents per GPU hour while the category median changed. Changing listings can move an index.',
'Our original prediction ranges were too narrow. Human-guided calibration widened them without changing the middle. Coverage rose from sixty-four point seven to seventy-five point four two percent. The uncertainty includes no improvement, and later November checks did not confirm the gain.',
'Four agents propose, test and record forecasting ideas. Later human-guided models failed their checks. Rejections remain visible, and our frozen submission stays unchanged.',
'Exa searched inside the loop. Three agents wrote shared past dot dev memory; two read it. Modal ran eight jobs. Memory matched local accuracy, but was slower.',
'White shows recorded prices. Green and gold overlap because our middle prediction matches Pacific. We changed the prediction bounds, not actual prices. Future actual prices are unavailable.',
'For twenty twenty-nine: H one hundred rents, ninety-eight cents to two dollars fifty-nine; A one hundred, forty-two cents to one dollar twenty per GPU hour. Assumed scenarios, not tested future prices.',
'After setup, one command rebuilds saved forecasts offline. Sources, frozen protocols, official scores and failures are public. Better historical coverage is measured; a forecasting victory is not proven.'
]
silent=OUT/'demo-silent.webm'
if not silent.exists():silent.write_bytes((OUT/'demo.webm').read_bytes())
probe=subprocess.run([FFMPEG,'-i',str(silent)],capture_output=True,text=True).stderr
m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',probe);assert m,probe
video_seconds=int(m[1])*3600+int(m[2])*60+float(m[3]);assert 90<video_seconds<120
scenes=json.loads((OUT/'recording-scene-times.json').read_text());assert len(scenes)==len(TEXTS)
starts=[0]+[x['start'] for x in scenes[1:]]
SEGMENTS=[(start,(starts[i+1] if i+1<len(starts) else video_seconds)-.12,TEXTS[i]) for i,start in enumerate(starts)]
(OUT/'narration-script.json').write_text(json.dumps({'disclosure':'AI-generated voice','model':'gpt-4o-mini-tts','voice':'coral','segments':SEGMENTS},indent=2)+'\n')
rate=24000;timeline=bytearray(int(video_seconds*rate)*2);reports=[]
client=None
for i,(start,end,text) in enumerate(SEGMENTS):
 key=hashlib.sha256(('coral|'+text).encode()).hexdigest();source=CACHE/(key+'.wav')
 if not source.exists():
  if client is None:client=OpenAI(api_key=os.environ['OPENAI_API_KEY'])
  response=client.audio.speech.create(model='gpt-4o-mini-tts',voice='coral',input=text,response_format='wav',instructions='Clear, warm, confident documentary narration. Brisk natural pace. Do not exaggerate research claims.')
  source.write_bytes(response.content)
 with wave.open(str(source),'rb') as f:duration=len(f.readframes(f.getnframes()))/(f.getframerate()*f.getnchannels()*f.getsampwidth())
 speed=max(1,duration/(end-start-.2));assert speed<1.65,(i,duration,speed)
 adjusted=CACHE/f'segment-{i}.wav'
 subprocess.run([FFMPEG,'-y','-v','error','-i',str(source),'-af',f'atempo={speed}','-ar',str(rate),'-ac','1','-c:a','pcm_s16le',str(adjusted)],check=True)
 with wave.open(str(adjusted),'rb') as f:pcm=f.readframes(f.getnframes())
 pos=int(start*rate)*2;assert pos+len(pcm)<=int(end*rate)*2
 timeline[pos:pos+len(pcm)]=pcm
 reports.append({'segment':i,'start':start,'end':end,'source_seconds':duration,'speed':speed,'audio_sha256':hashlib.sha256(pcm).hexdigest()})
with wave.open(str(OUT/'narration.wav'),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(timeline)
silent=OUT/'demo-silent.webm'
if not silent.exists():silent.write_bytes((OUT/'demo.webm').read_bytes())
subprocess.run([FFMPEG,'-y','-v','error','-i',str(silent),'-i',str(OUT/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','libopus','-b:a','96k','-t',str(video_seconds),str(OUT/'demo-narrated.webm')],check=True)
(OUT/'narration-report.json').write_text(json.dumps({'duration_seconds':video_seconds,'audio':True,'disclosure':'AI-generated narration spoken at opening','segments':reports},indent=2)+'\n')
print('NARRATED_DEMO_CREATED')
