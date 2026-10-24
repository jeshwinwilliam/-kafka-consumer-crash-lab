#!/usr/bin/env python3
import argparse,datetime,hashlib,json,os,subprocess,sys,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1]; J='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home/bin/java'; CP=f'{R}/target/classes:{R}/target/dependency/*'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(args,**kw): return subprocess.run(args,text=True,capture_output=True,timeout=90,**kw)
def hashes():
 return {str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if p.is_file() and 'target' not in p.parts and 'results' not in p.parts}
def base_manifest():
 imgs=run(['docker','image','inspect','apache/kafka:4.1.2','postgres:17.11-bookworm','--format','{{.Id}} {{join .RepoDigests " "}}']).stdout.splitlines()
 return {'frozenAt':now(),'javaExecutable':J,'javaVersion':run([J,'-version']).stderr,'pythonExecutable':sys.executable,'pythonVersion':sys.version,'mavenVersion':run(['mvn','-version']).stdout,'sourceConfigurationSchemaHashes':hashes(),'imageDigests':imgs,'environment':{k:os.environ.get(k) for k in ['CRASHLAB_KAFKA_BOOTSTRAP','CRASHLAB_JDBC_URL']}}
def write(d,n,x): (d/n).write_text(json.dumps(x,indent=2,sort_keys=True))
def m2(case,attempt,frozen):
 p=run([sys.executable,str(R/'scripts/run_m2.py'),case]); rec={'timestamp':now(),'case':case,'attempt':attempt,'controllerCommand':[sys.executable,str(R/'scripts/run_m2.py'),case],'exitCode':p.returncode,'controllerStdout':p.stdout,'controllerStderr':p.stderr,'frozenManifest':frozen}
 try: out=json.loads(p.stdout.strip().splitlines()[-1]); d=Path(out['path']); rec['resultPath']=str(d); rec['reportedStatus']=out['status']; write(d,'m4-trial-manifest.json',rec); return rec
 except Exception as e: rec['reportedStatus']='invalid';rec['parseError']=repr(e);return rec
def conc(case,attempt,frozen):
 runid=f'm4-{case}-{attempt:02d}-{uuid.uuid4().hex[:10]}';d=R/'results'/runid;d.mkdir();mode='commit' if case=='8' else 'rollback';cmd=[J,'-cp',CP,'com.jeshwin.crashlab.M3ConcurrencyHarness',mode,runid];p=run(cmd);(d/'harness.stdout.ndjson').write_text(p.stdout);(d/'harness.stderr.log').write_text(p.stderr); events=[]
 for line in p.stdout.splitlines():
  try: events.append(json.loads(line))
  except: pass
 final=next((x for x in reversed(events) if x.get('event')=='FINAL'),None); valid=any(x.get('event')=='CONTENTION_CONFIRMED' for x in events)
 ok=final is not None and valid and ((case=='8' and final.get('aApplied') and not final.get('bApplied') and final.get('balance')==100) or (case=='9' and final.get('aApplied') and final.get('bApplied') and final.get('balance')==100))
 rec={'timestamp':now(),'case':case,'attempt':attempt,'runId':runid,'command':cmd,'exitCode':p.returncode,'contentionObserved':valid,'final':final,'status':'pass' if p.returncode==0 and ok else ('invalid' if not valid else 'fail'),'evidencePath':str(d),'frozenManifest':frozen}
 write(d,'result.json',rec);write(d,'manifest.json',rec);return rec
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--count',type=int,default=10);ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=False); frozen=base_manifest();write(out,'frozen-source-manifest.json',frozen); all=[]
 for c in ['2','3','4','5','6']:
  for i in range(1,a.count+1): all.append(m2(c,i,str(out/'frozen-source-manifest.json')))
 for c in ['8','9']:
  for i in range(1,a.count*2+1): all.append(conc(c,i,str(out/'frozen-source-manifest.json')))
 summary={'createdAt':now(),'planned':a.count*5+a.count*2*2,'trials':all};write(out,'campaign-index.json',summary);print(json.dumps({'out':str(out),'counts':{c:sum(x['case']==c and x.get('reportedStatus',x.get('status'))=='pass' for x in all) for c in ['2','3','4','5','6','8','9']}}))
if __name__=='__main__':main()
