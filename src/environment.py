"""Load explicitly allowed local credentials without evaluating shell syntax."""
import os
from pathlib import Path
KEYS={'OPENAI_API_KEY','EXA_API_KEY','PAST_API_KEY','MODAL_TOKEN_ID','MODAL_TOKEN_SECRET','VERCEL_TOKEN','NETLIFY_AUTH_TOKEN'}
def load_environment(path=None):
    path=Path(path) if path else Path(__file__).resolve().parents[1]/'.env'
    if not path.is_file(): return
    for raw in path.read_text().splitlines():
        line=raw.strip()
        if not line or line.startswith('#'): continue
        if line.startswith('export '):line=line[7:].strip()
        if '=' not in line: raise ValueError('Invalid .env entry: expected KEY=value; secret values are never printed')
        key,value=line.split('=',1);key=key.strip();value=value.strip()
        if key not in KEYS: raise ValueError('Unsupported credential variable in .env')
        if len(value)>=2 and value[0]==value[-1] and value[0] in ('"',"'"):value=value[1:-1]
        if value and not os.environ.get(key):os.environ[key]=value
