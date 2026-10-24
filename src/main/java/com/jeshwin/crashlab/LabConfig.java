package com.jeshwin.crashlab;
/** Runtime endpoints are environment-overridable so fresh reproduction does not target the original lab. */
public final class LabConfig {
    private LabConfig() {}
    public static String kafkaBootstrap() { return System.getenv().getOrDefault("CRASHLAB_KAFKA_BOOTSTRAP", "localhost:9092"); }
    public static String jdbcUrl() { return System.getenv().getOrDefault("CRASHLAB_JDBC_URL", "jdbc:postgresql://localhost:5433/crashlab?connectTimeout=10&socketTimeout=10"); }
    public static String dbUser() { return System.getenv().getOrDefault("CRASHLAB_DB_USER", "crashlab"); }
    public static String dbPassword() { return System.getenv().getOrDefault("CRASHLAB_DB_PASSWORD", "local-lab-only"); }
}
