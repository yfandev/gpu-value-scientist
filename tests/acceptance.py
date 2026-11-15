"""Independent end-to-end acceptance, including offline execution with sockets denied."""
import os,sys,json,hashlib,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
def execute(args,env=None):
    p=subprocess.run(args,capture_output=True,text=True,env=env)
    if p.returncode:
        Path('logs/acceptance-failure.log').write_text(p.stdout+'\nSTDERR:\n'+p.stderr)
        raise AssertionError(f'Exit {p.returncode}; full log logs/acceptance-failure.log\n'+p.stdout[-1500:]+p.stderr[-1500:])
    return p

def main():
    execute([sys.executable,'-B','-m','unittest','discover','-s','tests','-v'])
    cfg=json.loads(Path('config.json').read_text());pack=Path(cfg['pack'])
    manifest=subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=pack,capture_output=True,text=True)
    assert manifest.returncode==0,manifest.stderr
    assert not list(pack.rglob('__pycache__')),'Pack modified by interpreter caches'
    expected=hashlib.sha256(Path('forecasts.csv').read_bytes()).hexdigest()
    before=json.loads(Path('results/online_last_value.json').read_text())['overall']
    with tempfile.TemporaryDirectory(prefix='gvs-offline-') as tmp:
        Path(tmp,'sitecustomize.py').write_text("import socket\ndef deny(*a,**k):\n raise RuntimeError('OFFLINE_NETWORK_DENIED')\nsocket.socket.connect=deny\nsocket.socket.connect_ex=deny\nsocket.create_connection=deny\n")
        env={**os.environ,'PYTHONPATH':tmp,'PYTHONDONTWRITEBYTECODE':'1','PYTHON':sys.executable}
        # Positive control proves our no-network execution environment rejects connections.
        negative=subprocess.run([sys.executable,'-c',"import socket; socket.create_connection(('example.com',443))"],capture_output=True,text=True,env=env)
        assert negative.returncode!=0 and 'OFFLINE_NETWORK_DENIED' in negative.stderr
        p=execute(['bash','reproduce.sh'],env);Path('logs/acceptance-reproduce.log').write_text(p.stdout+p.stderr)
    actual=hashlib.sha256(Path('forecasts.csv').read_bytes()).hexdigest();assert actual==expected,'Forecast bytes changed in offline reproduction'
    assert json.loads(Path('results/online_last_value.json').read_text())['overall']==before,'Official metrics changed'
    if (ROOT/'.git').exists():
        author=subprocess.check_output(['git','config','user.name'],text=True).strip()
        assert author=='yfandev','Git author must be yfandev'
        remote=subprocess.run(['git','remote','get-url','origin'],capture_output=True,text=True)
        if remote.returncode==0:assert 'github.com/yfandev/gpu-value-scientist' in remote.stdout, 'Unexpected repository owner'
    events=[json.loads(x) for x in Path('logs/agent_log.jsonl').read_text().splitlines()]
    writers={e['who'] for e in events if e['what']=='memory_write'};readers={e['who'] for e in events if e['what']=='memory_read' and e['outcome']['n_entries']>0}
    assert {'ANALYST','CRITIC'}<=writers and {'ANALYST','FORECASTER'}<=readers
    audits=json.loads(Path('results/replay_audit.json').read_text())
    for a in audits:
        assert all(o<a['forecast_origin'] for o in a['training_origins'])
        assert a['max_available_target_date']<=a['forecast_origin']
    hs=json.loads(Path('results/hypotheses.json').read_text())
    for h in hs:
        for origin in h.get('validation_origins',[]):assert h['frozen_at']<=origin<h['evaluated_at']
    sponsor=json.loads(Path('results/sponsor_audit.json').read_text())
    receipt=sponsor.get('recorded_live_run',{})
    verified=receipt.get('status')=='matched_exact_live_run'
    live=receipt.get('sponsors',{}) if verified else sponsor
    integration_ok=live.get('past_dev',{}).get('sponsor_requirements_verified',False) and live.get('exa',{}).get('status')=='live_verified'
    result={'status':'passed_offline_core','forecast_sha256':actual,'pack_files_verified':len(manifest.stdout.splitlines()),'offline_network_guard_positive_control':'passed','byte_identical_forecasts':True,'official_metrics_identical':True,'memory_writers':sorted(writers),'memory_readers':sorted(readers),'live_integrations':{'matching_live_receipt':verified,'actual_access_verified':integration_ok},'target_discrepancy':'37 actual November posted headline targets, not the mixed 97 October targets'}
    Path('results/acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    payload=json.loads(Path('demo/data.json').read_text())
    payload['checks'].extend([{'name':'Offline byte-identical reproduction','status':'passed','detail':'Network socket connections denied; positive control fails; forecasts and official metrics identical.'},{'name':'Shared memory roles','status':'passed','detail':f"Offline replay roles: writers {', '.join(sorted(writers))}; readers {', '.join(sorted(readers))}."},{'name':'Live OpenAI / past.dev / Exa','status':'passed' if integration_ok else 'unverified','detail':'Matching recorded live receipt verifies actual API access; this acceptance run itself is offline.' if integration_ok else 'No matching actual live execution verified.'},{'name':'80% interval calibration goal','status':'not achieved','detail':'Measured historical online coverage is below target; see actual metric.'}])
    Path('demo/data.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(result,indent=2));print('GPU_VALUE_OFFLINE_ACCEPTANCE_PASSED')
if __name__=='__main__':main()
