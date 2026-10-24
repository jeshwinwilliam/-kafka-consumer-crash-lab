package com.jeshwin.crashlab;

import java.sql.DriverManager;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.admin.Admin;

public final class ConnectivityCheck {
    public static void main(String[] args) throws Exception {
        Properties kafka = new Properties();
        kafka.put("bootstrap.servers", LabConfig.kafkaBootstrap());
        kafka.put("default.api.timeout.ms", "15000");
        kafka.put("request.timeout.ms", "10000");

        try (Admin admin = Admin.create(kafka)) {
            var topic = admin.describeTopics(List.of("account-credits"))
                    .allTopicNames().get(20, TimeUnit.SECONDS)
                    .get("account-credits");

            if (topic.partitions().size() != 1
                    || topic.partitions().get(0).replicas().size() != 1) {
                throw new IllegalStateException("Expected one partition and one replica");
            }
            System.out.println("KAFKA_OK topic=account-credits partitions=1 replicas=1");
        }

        DriverManager.setLoginTimeout(10);
        try (var db = DriverManager.getConnection(LabConfig.jdbcUrl(), LabConfig.dbUser(), LabConfig.dbPassword());
             var query = db.prepareStatement(
                    "SELECT balance FROM accounts WHERE account_id = ?")) {
            query.setString(1, "account-001");
            try (var rows = query.executeQuery()) {
                if (!rows.next()) {
                    throw new IllegalStateException("Missing account-001");
                }
                long balance = rows.getLong(1);
                if (balance != 0) {
                    throw new IllegalStateException("Expected balance 0, found " + balance);
                }
                System.out.println("POSTGRES_OK account=account-001 balance=0");
            }
        }
        System.out.println("CONNECTIVITY_CHECK_PASSED");
    }
}
