#!/usr/bin/env python3
"""Versioned replacement evidence controller for fresh M4 cases 10–12.
It deliberately pins all Java, PostgreSQL, and Kafka work to m4fresh."""
import datetime, hashlib, json, os, subprocess, sys, uuid
from pathlib import Path
R = Path(__file__).resolve().parents[1]
BUILD = R / 'results/m4/rebuilt-frozen-source-20261017b/source'
JAVA = Path('/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home/bin/java')
CP = f'{BUILD}/target/classes:{BUILD}/target/dependency/*'
PROJECT='kafka-crash-lab-m4fresh'; COMPOSE_FILE=R/'compose.m4-fresh.yaml'; KAFKA_PORT='19092'; PG_PORT='15433'
COMPOSE=['docker','compose','-p',PROJECT,'-f',str(COMPOSE_FILE)]
ENV=os.environ.copy(); ENV.update({'M4_KAFKA_PORT':KAFKA_PORT,'M4_POSTGRES_PORT':PG_PORT,'CRASHLAB_KAFKA_BOOTSTRAP':f'localhost:{KAFKA_PORT}','CRASHLAB_JDBC_URL':f'jdbc:postgresql://localhost:{PG_PORT}/crashlab?connectTimeout=10&socketTimeout=10'})
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(argv, timeout=75):
 p=subprocess.run(argv,text=True,capture_output=True,env=ENV,timeout=timeout); return {'timestamp':now(),'argv':argv,'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def j(cls,*args,timeout=75): return run([str(JAVA),'-cp',CP,cls,*map(str,args)],timeout)
def parse(rec): return json.loads(rec['stdout'])
def save_cmd(d,name,rec,commands):
 (d/f'{name}.stdout').write_text(rec['stdout']); (d/f'{name}.stderr').write_text(rec['stderr']); commands.append({'name':name,'timestamp':rec['timestamp'],'argv':rec['argv'],'exitCode':rec['exitCode'],'stdoutPath':f'{name}.stdout','stderrPath':f'{name}.stderr'}); return rec
def docker(name,*args): return run(COMPOSE+list(args))
def fixture(d, commands, runid, topic, group, event, account):
 x=save_cmd(d,'fixture',j('com.jeshwin.crashlab.M1FixtureTool',topic,group,event,account,runid),commands)
 if x['exitCode'] != 0: raise RuntimeError('fixture failed')
 data=parse(x); (d/'fixture.json').write_text(json.dumps(data,indent=2)); return data
def inspect(d,commands,name,topic,group,account,event):
 x=save_cmd(d,name,j('com.jeshwin.crashlab.M1Inspector',topic,group,account,event,'dedup-db-first',name),commands)
 if x['exitCode'] != 0: raise RuntimeError(f'inspector {name} failed')
 data=parse(x); (d/f'{name}.json').write_text(json.dumps(data,indent=2)); return data
def dbsnap(d,commands,name,account,event):
 x=save_cmd(d,name,j('com.jeshwin.crashlab.M4DbTool','snapshot',account,event),commands)
 if x['exitCode'] != 0: raise RuntimeError(f'db snapshot {name} failed')
 return parse(x)
def compose_identity(d,commands):
 for n,a in [('compose-config',['config']),('compose-ps',['ps','--format','json']),('kafka-internal-metadata',['exec','-T','kafka','/opt/kafka/bin/kafka-topics.sh','--bootstrap-server','kafka:9092','--list'])]: save_cmd(d,n,docker(n,*a),commands)
def hashes():
 ah=BUILD.parent/'artifact-hashes.sha256'; bh=BUILD.parent/'source-hash-comparison.json'; return {'buildRoot':str(BUILD),'classpath':CP,'artifactHashFile':str(ah),'artifactHashFileSha256':sha(ah) if ah.exists() else None,'sourceComparison':str(bh),'sourceComparisonSha256':sha(bh) if bh.exists() else None,'controllerSha256':sha(Path(__file__))}
def group(d,commands,name,topic,g): return save_cmd(d,name,docker(name,'exec','-T','kafka','/opt/kafka/bin/kafka-consumer-groups.sh','--bootstrap-server','kafka:9092','--group',g,'--describe'),commands)
def main(case):
 runid=f'm4-fresh-corrected-v2-case{case}-{uuid.uuid4().hex[:12]}'; d=R/'results/m4/fresh-corrected-v2'/runid; d.mkdir(parents=True); topic=f'account-credits-{runid}'; groupid=f'group-{runid}'; event=f'event-{runid}'; account=f'account-{runid}'; commands=[]
 manifest={'schemaVersion':2,'createdAt':now(),'experimentTimeStarted':now(),'case':int(case),'runId':runid,'environment':{'composeProject':PROJECT,'composeFile':str(COMPOSE_FILE),'kafkaBootstrap':ENV['CRASHLAB_KAFKA_BOOTSTRAP'],'jdbcUrl':ENV['CRASHLAB_JDBC_URL'],'java':str(JAVA)},'sourceArtifactProvenance':hashes(),'fixture':{'topic':topic,'group':groupid,'eventId':event,'accountId':account},'commands':commands}
 try:
  compose_identity(d,commands); f=fixture(d,commands,runid,topic,groupid,event,account); manifest['fixture']['metadata']=f
  if case=='10':
   deleted=parse(save_cmd(d,'delete-account',j('com.jeshwin.crashlab.M4DbTool','delete-account',account),commands)); pre=group(d,commands,'pre-failure-group',topic,groupid); c=save_cmd(d,'missing-account-consumer',j('com.jeshwin.crashlab.CrashConsumer',topic,groupid,event,account,'dedup-db-first','none',runid,'false'),commands); db=dbsnap(d,commands,'post-failure-db',account,event); off=group(d,commands,'post-failure-group',topic,groupid); ok=deleted.get('deletedAccounts')==1 and c['exitCode']!=0 and db['balance'] is None and db['dedupCount']==0 and f['offset']==0 and ' 0 ' in off['stdout']; manifest.update({'observed':{'deleteAccount':deleted,'consumerExit':c['exitCode'],'postFailureDb':db,'postFailureOffsetRaw':off['stdout']},'expected':{'accountAbsent':True,'dedupCount':0,'committedOffset':f['offset']},'status':'pass' if ok else 'fail'})
  elif case=='11':
   e2=f'event2-{runid}'; p2=parse(save_cmd(d,'second-producer',j('com.jeshwin.crashlab.M3Producer',topic,e2,account),commands)); c1=save_cmd(d,'consumer-first',j('com.jeshwin.crashlab.CrashConsumer',topic,groupid,event,account,'dedup-db-first','none',runid,'false'),commands); c2=save_cmd(d,'consumer-second',j('com.jeshwin.crashlab.CrashConsumer',topic,groupid,e2,account,'dedup-db-first','none',runid,'false'),commands); final=inspect(d,commands,'final-inspector',topic,groupid,account,e2); count=parse(save_cmd(d,'two-event-dedup-count',j('com.jeshwin.crashlab.M4DbTool','count',event,e2),commands)); off=group(d,commands,'final-group',topic,groupid); ok=c1['exitCode']==0 and c2['exitCode']==0 and final['balance']==200 and final['committedOffset']>p2['offset'] and count['dedupCount']==2; manifest['fixture']['secondEventId']=e2; manifest.update({'observed':{'secondProducer':p2,'consumerExits':[c1['exitCode'],c2['exitCode']],'final':final,'scopedDedup':count,'groupRaw':off['stdout']},'expected':{'balance':200,'dedupCount':2,'committedBeyondOffset':p2['offset']},'status':'pass' if ok else 'fail'})
  else:
   c1=save_cmd(d,'initial-consumer',j('com.jeshwin.crashlab.CrashConsumer',topic,groupid,event,account,'dedup-db-first','none',runid,'false'),commands); pre=inspect(d,commands,'pre-delete-inspector',topic,groupid,account,event); dr=parse(save_cmd(d,'delete-dedup-returning',j('com.jeshwin.crashlab.M4DbTool','delete-dedup',event),commands)); postdel=dbsnap(d,commands,'post-delete-db',account,event); reset=save_cmd(d,'group-reset',docker('group-reset','exec','-T','kafka','/opt/kafka/bin/kafka-consumer-groups.sh','--bootstrap-server','kafka:9092','--group',groupid,'--topic',f'{topic}:0','--reset-offsets','--to-offset','0','--execute'),commands); prer=inspect(d,commands,'pre-replay-inspector',topic,groupid,account,event); c2=save_cmd(d,'replay-consumer',j('com.jeshwin.crashlab.CrashConsumer',topic,groupid,event,account,'dedup-db-first','none',runid,'false'),commands); final=inspect(d,commands,'final-inspector',topic,groupid,account,event); off=group(d,commands,'final-group',topic,groupid); ok=c1['exitCode']==0 and dr.get('deletedDedup')==1 and pre['balance']==100 and postdel['balance']==100 and postdel['dedupCount']==0 and c2['exitCode']==0 and final['balance']==200 and final['dedupCount']==1; manifest.update({'observed':{'initialExit':c1['exitCode'],'preDelete':pre,'deleteResult':dr,'postDeletionDb':postdel,'resetExit':reset['exitCode'],'preReplay':prer,'replayExit':c2['exitCode'],'final':final,'groupRaw':off['stdout']},'expected':{'preDeleteBalance':100,'deleteRows':1,'postDeleteDedup':0,'postReplayBalance':200,'postReplayDedup':1},'status':'pass' if ok else 'fail'})
 except Exception as e: manifest.update({'status':'invalid','error':repr(e)})
 manifest['experimentTimeFinished']=now(); (d/'manifest.json').write_text(json.dumps(manifest,indent=2)); (d/'result.json').write_text(json.dumps(manifest,indent=2)); print(json.dumps({'path':str(d),'status':manifest['status']})); return 0 if manifest['status']=='pass' else 2
if __name__=='__main__':
 if len(sys.argv)!=2 or sys.argv[1] not in {'10','11','12'}: raise SystemExit('usage: run_m4_fresh_10_12_v2.py 10|11|12')
 raise SystemExit(main(sys.argv[1]))
