#!/usr/bin/env python3
import json,subprocess,sys,uuid,signal,time,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1];J='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home/bin/java';CP=f'{R}/target/classes:{R}/target/dependency/*';S='dedup-db-first'
def call(c,*a):return subprocess.run([J,'-cp',CP,c,*a],text=True,capture_output=True,check=True,timeout=50)
def snap(d,n,t,g,a,e):x=call('com.jeshwin.crashlab.M1Inspector',t,g,a,e,S,n);(d/(n+'.json')).write_text(x.stdout);return json.loads(x.stdout)
def child(t,g,e,a,s,b,r,o=False):return subprocess.Popen([J,'-cp',CP,'com.jeshwin.crashlab.CrashConsumer',t,g,e,a,s,b,r,str(o).lower()],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
def manifest():
 files=[x for x in R.rglob('*') if x.is_file() and 'target' not in x.parts and 'results' not in x.parts]
 h={str(x.relative_to(R)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}
 imgs=subprocess.run(['docker','image','inspect','apache/kafka:4.1.2','postgres:17.11-bookworm','--format','{{.RepoTags}} {{join .RepoDigests " "}}'],text=True,capture_output=True,check=True).stdout.splitlines()
 return {'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pythonExecutable':sys.executable,'python':sys.version,'java':subprocess.run([J,'-version'],text=True,capture_output=True).stderr,'maven':subprocess.run(['mvn','-version'],text=True,capture_output=True).stdout,'sourceHashes':h,'imageDigests':imgs}
def run(n,s,b='none',obs=False):
 r='m2-'+n+'-'+uuid.uuid4().hex[:10];d=R/'results'/r;d.mkdir();t='account-credits-'+r;g='group-'+r;e='event-'+r;a='account-'+r;m={'runId':r,'case':n,'strategy':s,'commands':[f'{J} -cp <classes:dependencies> CrashConsumer',f'{J} -cp <classes:dependencies> M1FixtureTool',f'{J} -cp <classes:dependencies> M1Inspector'],'evidencePath':str(d),**manifest()}
 try:
  f=json.loads(call('com.jeshwin.crashlab.M1FixtureTool',t,g,e,a,r).stdout);(d/'fixture.json').write_text(json.dumps(f));pre=snap(d,'baseline',t,g,a,e);p=child(t,g,e,a,s,b,r)
  if b=='none':o,er=p.communicate(timeout=50);(d/'child.stdout.log').write_text(o);(d/'child.stderr.log').write_text(er);z=snap(d,'final',t,g,a,e);ok=p.returncode==0 and z['balance']==100 and z['committedOffset']==f['offset']+1 and z['dedupCount']==(1 if s=='dedup-db-first' else 0);m.update(status='pass' if ok else 'fail',pre=pre,final=z,exit=p.returncode)
  else:
   ls=[];end=time.time()+50
   while time.time()<end:
    l=p.stdout.readline()
    if l:ls.append(l)
    if l.startswith('BARRIER ') and all(x in l for x in [f'runId={r}',f'eventId={e}',f'strategy={s}',f'phase={b}',f'offset={f["offset"]}']):break
   else:raise RuntimeError('missing validated barrier')
   (d/'controller-events.log').write_text(''.join(ls));p.kill();p.wait(15);o,er=p.communicate();(d/'killed.stdout.log').write_text(o);(d/'killed.stderr.log').write_text(er);k=snap(d,'post-kill-pre-restart',t,g,a,e);q=child(t,g,e,a,s,'none',r,obs);o2,e2=q.communicate(timeout=50);(d/'restart.stdout.log').write_text(o2);(d/'restart.stderr.log').write_text(e2);z=snap(d,'post-restart',t,g,a,e)
   if s=='db-first':ok=k['balance']==100 and k['committedOffset']==f['offset'] and z['balance']==200 and z['committedOffset']==f['offset']+1 and f'offset={f["offset"]}' in o2
   elif b=='after-offset-commit':ok=k['balance']==0 and k['committedOffset']==f['offset']+1 and z['balance']==0 and 'NO_RECORD_OBSERVED' in o2
   elif b=='before-db-commit':ok=k['balance']==0 and k['dedupCount']==0 and k['committedOffset']==f['offset'] and z['balance']==100 and z['dedupCount']==1 and z['committedOffset']==f['offset']+1
   elif b=='after-db-commit':ok=k['balance']==100 and k['dedupCount']==1 and k['committedOffset']==f['offset'] and z['balance']==100 and z['dedupCount']==1 and z['committedOffset']==f['offset']+1 and f'offset={f["offset"]}' in o2
   else:ok=k['balance']==100 and k['dedupCount']==1 and k['committedOffset']==f['offset']+1 and z['balance']==100 and 'NO_RECORD_OBSERVED' in o2
   m.update(status='pass' if ok else 'fail',pre=pre,postKill=k,final=z,killedExit=p.returncode,restartExit=q.returncode,barrier=ls[-1].strip())
 except Exception as x:m.update(status='invalid',error=repr(x))
 (d/'result.json').write_text(json.dumps(m,indent=2));print(json.dumps({'path':str(d),'status':m['status']}));return 0 if m['status']=='pass' else 2
if __name__=='__main__':
 q={'1a':('db-first','none',False),'1b':('offset-first','none',False),'1c':('dedup-db-first','none',False),'2':('db-first','after-db-commit',False),'3':('offset-first','after-offset-commit',True),'4':('dedup-db-first','after-db-commit',False),'5':('dedup-db-first','before-db-commit',False),'6':('dedup-db-first','after-both-commits',True)}
 if len(sys.argv)!=2 or sys.argv[1] not in q:raise SystemExit('usage')
 raise SystemExit(run(sys.argv[1],*q[sys.argv[1]]))
