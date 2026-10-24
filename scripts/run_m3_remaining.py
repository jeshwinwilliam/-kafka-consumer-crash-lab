#!/usr/bin/env python3
import json,subprocess,uuid,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];J='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home/bin/java';CP=f'{R}/target/classes:{R}/target/dependency/*'
def call(c,*a,check=True):return subprocess.run([J,'-cp',CP,c,*a],text=True,capture_output=True,check=check,timeout=50)
def sh(*a):return subprocess.run(a,text=True,capture_output=True,check=True,timeout=50)
case=sys.argv[1];r='m3-'+case+'-'+uuid.uuid4().hex[:10];d=R/'results'/r;d.mkdir();t='account-credits-'+r;g='group-'+r;e='event-'+r;a='account-'+r
try:
 f=json.loads(call('com.jeshwin.crashlab.M1FixtureTool',t,g,e,a,r).stdout)
 if case=='10':
  sh('docker','compose','-f',str(R/'compose.yaml'),'exec','-T','postgres','psql','-U','crashlab','-d','crashlab','-c',f"DELETE FROM accounts WHERE account_id='{a}'")
  x=call('com.jeshwin.crashlab.CrashConsumer',t,g,e,a,'dedup-db-first','none',r,'false',check=False);s=json.loads(call('com.jeshwin.crashlab.M1Inspector',t,g,a,e,'dedup-db-first','final').stdout) if False else None
  q=sh('docker','compose','-f',str(R/'compose.yaml'),'exec','-T','postgres','psql','-At','-U','crashlab','-d','crashlab','-c',f"SELECT count(*) FROM processed_events WHERE handler_scope='dedup-db-first' AND event_id='{e}'").stdout.strip();res={'case':10,'exit':x.returncode,'dedupCount':int(q),'expectedOffset':f['offset'],'stdout':x.stdout,'stderr':x.stderr,'status':'pass' if x.returncode!=0 and q=='0' else 'fail'}
 elif case=='11':
  e2='event2-'+r;p=json.loads(call('com.jeshwin.crashlab.M3Producer',t,e2,a).stdout);x1=call('com.jeshwin.crashlab.CrashConsumer',t,g,e,a,'dedup-db-first','none',r,'false');x2=call('com.jeshwin.crashlab.CrashConsumer',t,g,e2,a,'dedup-db-first','none',r,'false');s=json.loads(call('com.jeshwin.crashlab.M1Inspector',t,g,a,e2,'dedup-db-first','final').stdout);q=sh('docker','compose','-f',str(R/'compose.yaml'),'exec','-T','postgres','psql','-At','-U','crashlab','-d','crashlab','-c',f"SELECT count(*) FROM processed_events WHERE handler_scope='dedup-db-first' AND event_id IN ('{e}','{e2}')").stdout.strip();res={'case':11,'first':f,'second':p,'final':s,'dedupTotal':int(q),'status':'pass' if s['balance']==200 and s['committedOffset']==2 and q=='2' else 'fail'}
 else:
  call('com.jeshwin.crashlab.CrashConsumer',t,g,e,a,'dedup-db-first','none',r,'false');pre=json.loads(call('com.jeshwin.crashlab.M1Inspector',t,g,a,e,'dedup-db-first','pre-delete').stdout);sh('docker','compose','-f',str(R/'compose.yaml'),'exec','-T','postgres','psql','-U','crashlab','-d','crashlab','-c',f"DELETE FROM processed_events WHERE handler_scope='dedup-db-first' AND event_id='{e}'");sh('docker','compose','-f',str(R/'compose.yaml'),'exec','-T','kafka','/opt/kafka/bin/kafka-consumer-groups.sh','--bootstrap-server','localhost:9092','--group',g,'--topic',f'{t}:0','--reset-offsets','--to-offset','0','--execute');call('com.jeshwin.crashlab.CrashConsumer',t,g,e,a,'dedup-db-first','none',r,'false');post=json.loads(call('com.jeshwin.crashlab.M1Inspector',t,g,a,e,'dedup-db-first','post-replay').stdout);res={'case':12,'pre':pre,'post':post,'status':'pass' if pre['balance']==100 and post['balance']==200 and post['dedupCount']==1 else 'fail'}
except Exception as x:res={'case':case,'status':'invalid','error':repr(x)}
(d/'result.json').write_text(json.dumps(res,indent=2));print(json.dumps({'path':str(d),'status':res['status']}));raise SystemExit(0 if res['status']=='pass' else 2)
