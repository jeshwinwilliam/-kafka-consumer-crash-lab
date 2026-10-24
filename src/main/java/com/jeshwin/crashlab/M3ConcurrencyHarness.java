package com.jeshwin.crashlab;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;

/** M4 concurrency witness: A holds a dedup transaction while B uses DatabaseWork.begin. */
public final class M3ConcurrencyHarness {
  static long now(){ return System.currentTimeMillis(); }
  static String q(String s){ return s == null ? "null" : "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n") + "\""; }
  static void emit(String event, String fields){ System.out.println("{\"timestamp\":"+now()+",\"event\":\""+event+"\""+fields+"}"); System.out.flush(); }
  static long pid(Connection c)throws Exception { try(var s=c.createStatement(); var r=s.executeQuery("select pg_backend_pid()")){r.next(); return r.getLong(1);} }
  static String isolation(Connection c)throws Exception { try(var s=c.createStatement(); var r=s.executeQuery("show transaction_isolation")){r.next();return r.getString(1);} }
  static void close(Connection c){try{if(c!=null&&!c.isClosed())c.close();}catch(Exception ignored){}}
  public static void main(String[] a)throws Exception {
    if(a.length!=2 || !(a[0].equals("commit")||a[0].equals("rollback"))) throw new IllegalArgumentException("usage: commit|rollback runId");
    String mode=a[0], run=a[1], id="event-"+run, acct="account-"+run;
    Connection ca=null, cb=null; ExecutorService ex=Executors.newSingleThreadExecutor(); Future<DatabaseWork.Outcome> fb=null;
    try {
      try(var d=DatabaseWork.open();var s=d.prepareStatement("insert into accounts(account_id,balance) values (?,0)")){s.setString(1,acct);s.executeUpdate();}
      ca=DatabaseWork.open(); cb=DatabaseWork.open(); long pa=pid(ca), pb=pid(cb);
      emit("PIDS",",\"runId\":"+q(run)+",\"eventId\":"+q(id)+",\"accountId\":"+q(acct)+",\"aPid\":"+pa+",\"bPid\":"+pb+",\"aIsolation\":"+q(isolation(ca))+",\"bIsolation\":"+q(isolation(cb)));
      DatabaseWork.Outcome ao=DatabaseWork.begin(ca,"dedup-db-first",id,acct);
      emit("A_HELD",",\"aApplied\":"+ao.applied()+",\"phase\":\"after-dedup-insertion-and-update-before-commit\"");
      Connection b=cb; fb=ex.submit(()->DatabaseWork.begin(b,"dedup-db-first",id,acct));
      boolean blocked=false; long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(12);
      try(var o=DatabaseWork.open(); var s=o.prepareStatement("select state,wait_event_type,wait_event,query,pg_blocking_pids(pid)::text from pg_stat_activity where pid=?")) {
        while(System.nanoTime()<deadline){
          s.setLong(1,pb); try(var r=s.executeQuery()){
            if(r.next()) {String blockers=r.getString(5); emit("OBSERVER",",\"aPid\":"+pa+",\"bPid\":"+pb+",\"state\":"+q(r.getString(1))+",\"waitEventType\":"+q(r.getString(2))+",\"waitEvent\":"+q(r.getString(3))+",\"query\":"+q(r.getString(4))+",\"blockingPids\":"+q(blockers)); if(blockers!=null && Arrays.stream(blockers.replace("{","").replace("}","").split(",")).anyMatch(x->x.trim().equals(Long.toString(pa)))) {blocked=true;break;}}
          }
          Thread.sleep(50);
        }
      }
      if(!blocked) { emit("INVALID",",\"reason\":\"pg_blocking_pids(B) never contained A before deadline\""); ca.rollback(); close(ca); ca=null; try{DatabaseWork.Outcome bo=fb.get(15,TimeUnit.SECONDS);bo.connection().rollback();bo.connection().close();}catch(Exception ignored){} throw new IllegalStateException("contention not observed"); }
      emit("CONTENTION_CONFIRMED",",\"aPid\":"+pa+",\"bPid\":"+pb);
      if(mode.equals("commit")) ca.commit(); else ca.rollback(); emit("A_RELEASED",",\"release\":"+q(mode)); close(ca);ca=null;
      DatabaseWork.Outcome bo=fb.get(15,TimeUnit.SECONDS); bo.connection().commit(); bo.connection().close(); close(cb);cb=null;
      long bal,cnt;try(var d=DatabaseWork.open();var bq=d.prepareStatement("select balance from accounts where account_id=?");var cq=d.prepareStatement("select count(*) from processed_events where handler_scope=? and event_id=?")){bq.setString(1,acct);try(var r=bq.executeQuery()){r.next();bal=r.getLong(1);}cq.setString(1,DatabaseWork.DEDUP_SCOPE);cq.setString(2,id);try(var r=cq.executeQuery()){r.next();cnt=r.getLong(1);}}
      emit("FINAL",",\"mode\":"+q(mode)+",\"aApplied\":"+ao.applied()+",\"bApplied\":"+bo.applied()+",\"balance\":"+bal+",\"dedupCount\":"+cnt);
    } finally { if(fb!=null&&!fb.isDone())fb.cancel(true); close(ca);close(cb);ex.shutdownNow(); }
  }
}
