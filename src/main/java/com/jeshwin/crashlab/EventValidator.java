package com.jeshwin.crashlab;
public final class EventValidator {
    private EventValidator() {}
    public static void validate(String key, String value, String eventId, String accountId) {
        if (!eventId.equals(key) || !(accountId + "|100").equals(value)) throw new IllegalArgumentException("Unexpected event or payload");
    }
}
