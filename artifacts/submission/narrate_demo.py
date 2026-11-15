"""Add cached AI narration to the final captured walkthrough; never touch forecasts."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,wave
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from environment import load_environment
load_environment()
import imageio_ffmpeg
from openai import OpenAI
OUT=ROOT/'artifacts/submission';CACHE=OUT/'narration';CACHE.mkdir(exist_ok=True)
FFMPEG=imageio_ffmpeg.get_ffmpeg_exe()
SEGMENTS=[
(0,7,'Can agents distinguish GPU value from a changing price index? This voice is AI generated.'),
(7,16,'One H one hundred record stayed at ninety-four cents per GPU hour while the category median changed. Changing listings can move an index.'),
(16,38,'Our original prediction ranges were too narrow. Human-guided calibration widened them without changing the middle. Historical coverage rose from sixty-five to seventy-five percent. Combined error fell four point three percent versus Pacific, but the uncertainty includes no improvement.'),
(38,52,'Four agents propose, test and record bounded forecasting ideas. The log keeps failures visible. Later, human-guided price-model studies failed their promotion checks. We rejected them and preserved the frozen submission.'),
(52,65,'Exa searches ran inside the research loop. Three agents wrote to past dot dev, and two read shared findings. Modal ran eight experiment jobs. Memory matched local accuracy, but was slower.'),
(65,81,'Here is the selected H one hundred forecast. White shows recorded advertised prices. Green and gold overlap because our middle prediction matches Pacific. We changed the prediction bounds, not the actual prices. Future actual prices are not available.'),
(81,96,'Our central scenario expects lower H one hundred and A one hundred rents by twenty twenty-nine. Newer chips offer more work per GPU. Lower rental profits could reduce used equipment values. These are assumption-based scenarios, not measured future outcomes.'),
(96,111.8,'After setup, one command reproduces the saved forecasts offline. Frozen protocols, source rows and official scores are public. Our insight: a changing price index is not the same as a fixed GPU contract. Better historical coverage is measured; forecasting victory is not proven.')]
(OUT/'narration-script.json').write_text(json.dumps({'disclosure':'AI-generated voice','model':'gpt-4o-mini-tts','voice':'coral','segments':SEGMENTS},indent=2)+'\n')
rate=24000;timeline=bytearray(int(112.28*rate)*2);reports=[]
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
subprocess.run([FFMPEG,'-y','-v','error','-i',str(silent),'-i',str(OUT/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','libopus','-b:a','96k','-t','112.28',str(OUT/'demo-narrated.webm')],check=True)
(OUT/'narration-report.json').write_text(json.dumps({'duration_seconds':112.28,'audio':True,'disclosure':'AI-generated narration spoken at opening','segments':reports},indent=2)+'\n')
print('NARRATED_DEMO_CREATED')
