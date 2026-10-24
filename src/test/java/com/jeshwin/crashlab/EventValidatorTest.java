package com.jeshwin.crashlab;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
class EventValidatorTest { @Test void acceptsFixtureEvent(){EventValidator.validate("e","a|100","e","a");} @Test void rejectsWrongPayload(){assertThrows(IllegalArgumentException.class,()->EventValidator.validate("e","a|99","e","a"));} }
