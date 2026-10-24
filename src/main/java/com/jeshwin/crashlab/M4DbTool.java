package com.jeshwin.crashlab;
import java.sql.*;
/** Small M4 controller helper: DB state is read or changed through the configured environment only. */
public final class M4DbTool {
  private static String q(String v){return v==null?"null":"\""+v.replace("\\","\\\\").replace("\"","\\\"")+"\"";}
  public static void main(String[] a)throws Exception {
    if(a.length<2)throw new IllegalArgumentException("snapshot account event | delete-account account | delete-dedup event | count event1 event2");
    try(var d=DatabaseWork.open()){
      if(a[0].equals("delete-account")){try(var s=d.prepareStatement("delete from accounts where account_id=?")){s.setString(1,a[1]);System.out.println("{\"deletedAccounts\":"+s.executeUpdate()+"}");}return;}
      if(a[0].equals("delete-dedup")){try(var s=d.prepareStatement("delete from processed_events where handler_scope=? and event_id=?")){s.setString(1,DatabaseWork.DEDUP_SCOPE);s.setString(2,a[1]);System.out.println("{\"deletedDedup\":"+s.executeUpdate()+"}");}return;}
      if(a[0].equals("snapshot")){if(a.length!=3)throw new IllegalArgumentException("snapshot account event");Long b=null;long n;try(var s=d.prepareStatement("select balance from accounts where account_id=?")){s.setString(1,a[1]);try(var r=s.executeQuery()){if(r.next())b=r.getLong(1);}}try(var s=d.prepareStatement("select count(*) from processed_events where handler_scope=? and event_id=?")){s.setString(1,DatabaseWork.DEDUP_SCOPE);s.setString(2,a[2]);try(var r=s.executeQuery()){r.next();n=r.getLong(1);}}System.out.println("{\"accountId\":"+q(a[1])+",\"eventId\":"+q(a[2])+",\"balance\":"+(b==null?"null":b)+",\"dedupCount\":"+n+"}");return;}
      if(a[0].equals("count")){if(a.length!=3)throw new IllegalArgumentException("count event1 event2");try(var s=d.prepareStatement("select count(*) from processed_events where handler_scope=? and event_id in (?,?)")){s.setString(1,DatabaseWork.DEDUP_SCOPE);s.setString(2,a[1]);s.setString(3,a[2]);try(var r=s.executeQuery()){r.next();System.out.println("{\"dedupCount\":"+r.getLong(1)+"}");}}return;}
    }
    throw new IllegalArgumentException("unknown command");
  }
}
