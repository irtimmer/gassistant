# Copyright (C) 2019 Iwan Timmer
# SPDX-License-Identifier: Apache-2.0

from gpiozero import PWMLED

from google.assistant.library.event import EventType

LED_PIN = 25

class VoiceKit:

    def __init__(self, led_pin=LED_PIN):
        self.led = PWMLED(led_pin)

    def process_event(self, event):
        if event.type == EventType.ON_START_FINISHED:
            self.led.off()
        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self.led.on()
        elif event.type == EventType.ON_END_OF_UTTERANCE:
            self.led.pulse()
        elif event.type in [EventType.ON_CONVERSATION_TURN_FINISHED, EventType.ON_CONVERSATION_TURN_TIMEOUT, EventType.ON_NO_RESPONSE]:
            self.led.off()

def getInstance():
    return VoiceKit()
