package com.jeshwin.crashlab;
import java.sql.Connection;
import java.sql.DriverManager;
public final class DatabaseWork {
    public static final String DEDUP_SCOPE = "dedup-db-first";
    private DatabaseWork() {}
    public record Outcome(boolean applied, Connection connection) {}
    public static Connection open() throws Exception { return DriverManager.getConnection(LabConfig.jdbcUrl(), LabConfig.dbUser(), LabConfig.dbPassword()); }
    public static Outcome begin(String strategy, String eventId, String accountId) throws Exception { return begin(open(), strategy, eventId, accountId); }
    public static Outcome begin(Connection db, String strategy, String eventId, String accountId) throws Exception {
        db.setAutoCommit(false);
        try { boolean apply=!"dedup-db-first".equals(strategy);
            if (!apply) try (var s=db.prepareStatement("INSERT INTO processed_events(handler_scope,event_id,account_id,amount) VALUES (?,?,?,100) ON CONFLICT (handler_scope,event_id) DO NOTHING RETURNING event_id")) { s.setString(1,DEDUP_SCOPE);s.setString(2,eventId);s.setString(3,accountId);try(var r=s.executeQuery()){apply=r.next();} }
            if (!apply) try (var s=db.prepareStatement("SELECT account_id,amount FROM processed_events WHERE handler_scope=? AND event_id=?")) { s.setString(1,DEDUP_SCOPE);s.setString(2,eventId);try(var r=s.executeQuery()){if(!r.next())throw new IllegalStateException("Duplicate comparison row unavailable; retry required");if(r.getString(1)==null||r.getObject(2)==null)throw new IllegalStateException("Legacy dedup content is unknown");if(!accountId.equals(r.getString(1))||r.getLong(2)!=100)throw new IllegalStateException("Event identity content mismatch");} }
            if (apply) try (var s=db.prepareStatement("UPDATE accounts SET balance = balance + 100 WHERE account_id=?")) {s.setString(1,accountId);if(s.executeUpdate()!=1)throw new IllegalStateException("Expected one account");}
            return new Outcome(apply,db);
        } catch(Exception e){db.rollback();db.close();throw e;}
    }
}
