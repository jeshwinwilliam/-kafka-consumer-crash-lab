package com.jeshwin.crashlab;

import java.sql.DriverManager;
import java.time.Duration;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.apache.kafka.clients.admin.Admin;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.clients.consumer.OffsetAndMetadata;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.serialization.StringSerializer;

/** Creates one isolated M1 fixture and initializes its group at the target record. */
public final class M1FixtureTool {
    private M1FixtureTool() {}

    public static void main(String[] args) throws Exception {
        if (args.length != 5) {
            throw new IllegalArgumentException(
                "Usage: M1FixtureTool topic group eventId accountId runId");
        }
        String topic = args[0];
        String group = args[1];
        String eventId = args[2];
        String accountId = args[3];
        String runId = args[4];
        Properties adminConfig = new Properties();
        adminConfig.put("bootstrap.servers", LabConfig.kafkaBootstrap());
        adminConfig.put("default.api.timeout.ms", "15000");
        adminConfig.put("request.timeout.ms", "10000");
        try (Admin admin = Admin.create(adminConfig)) {
            admin.createTopics(java.util.List.of(new NewTopic(topic, 1, (short) 1)))
                .all().get(20, TimeUnit.SECONDS);
        }
        try (var db = DriverManager.getConnection(LabConfig.jdbcUrl(), LabConfig.dbUser(), LabConfig.dbPassword());
             var insert = db.prepareStatement(
                 "INSERT INTO accounts(account_id, balance) VALUES (?, 0)")) {
            insert.setString(1, accountId);
            if (insert.executeUpdate() != 1) {
                throw new IllegalStateException("Expected isolated account insertion");
            }
        }
        Properties producerConfig = new Properties();
        producerConfig.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, LabConfig.kafkaBootstrap());
        producerConfig.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        producerConfig.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        long offset;
        int partition;
        try (KafkaProducer<String, String> producer = new KafkaProducer<>(producerConfig)) {
            var metadata = producer.send(new ProducerRecord<>(topic, eventId, accountId + "|100"))
                .get(20, TimeUnit.SECONDS);
            producer.flush();
            offset = metadata.offset();
            partition = metadata.partition();
        }
        TopicPartition target = new TopicPartition(topic, partition);
        try (Admin admin = Admin.create(adminConfig)) {
            admin.alterConsumerGroupOffsets(group, Map.of(target, new OffsetAndMetadata(offset)))
                .all().get(20, TimeUnit.SECONDS);
            long committed = admin.listConsumerGroupOffsets(group)
                .partitionsToOffsetAndMetadata().get(20, TimeUnit.SECONDS)
                .get(target).offset();
            if (committed != offset) {
                throw new IllegalStateException("Group position was not initialized at target offset");
            }
        }
        System.out.println("{\"timestamp\":" + System.currentTimeMillis()
            + ",\"runId\":\"" + runId + "\",\"topic\":\"" + topic
            + "\",\"group\":\"" + group + "\",\"eventId\":\"" + eventId
            + "\",\"accountId\":\"" + accountId + "\",\"partition\":" + partition
            + ",\"offset\":" + offset + ",\"committedOffset\":" + offset + "}");
    }
}
