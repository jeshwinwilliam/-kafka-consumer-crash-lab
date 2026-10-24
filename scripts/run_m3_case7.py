#!/usr/bin/env python3
import subprocess,json,uuid,datetime,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];J='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home/bin/java';CP=f'{R}/target/classes:{R}/target/dependency/*'
def call(c,*a):return subprocess.run([J,'-cp',CP,c,*a],text=True,capture_output=True,check=True,timeout=50)
r='m3-7-'+uuid.uuid4().hex[:12];d=R/'results'/r;d.mkdir();t='account-credits-'+r;g='group-'+r;e='event-'+r;a='account-'+r
try:
 f=json.loads(call('com.jeshwin.crashlab.M1FixtureTool',t,g,e,a,r).stdout);p=json.loads(call('com.jeshwin.crashlab.M3Producer',t,e,a).stdout);(d/'producer.json').write_text(json.dumps({'first':f,'second':p},indent=2));o1=call('com.jeshwin.crashlab.CrashConsumer',t,g,e,a,'dedup-db-first','none',r,'false');o2=call('com.jeshwin.crashlab.CrashConsumer',t,g,e,a,'dedup-db-first','none',r,'false');(d/'consumer-1.log').write_text(o1.stdout+o1.stderr);(d/'consumer-2.log').write_text(o2.stdout+o2.stderr);s=json.loads(call('com.jeshwin.crashlab.M1Inspector',t,g,a,e,'dedup-db-first','final').stdout);(d/'final.json').write_text(json.dumps(s));ok=s['balance']==100 and s['dedupCount']==1 and s['committedOffset']==2;res={'case':7,'runId':r,'status':'pass' if ok else 'fail','producer':{'first':f,'second':p},'final':s,'commands':['M1FixtureTool','M3Producer','CrashConsumer x2','M1Inspector'],'python':sys.version};
except Exception as x:res={'case':7,'runId':r,'status':'invalid','error':repr(x)}
(d/'result.json').write_text(json.dumps(res,indent=2));print(json.dumps({'path':str(d),'status':res['status']}));raise SystemExit(0 if res['status']=='pass' else 2)
