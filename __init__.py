# Copyright 2017, Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from adapt.intent import IntentBuilder

from mycroft import MycroftSkill, intent_handler
from mycroft.messagebus.message import Message
from mycroft.audio import wait_while_speaking

import time


class NapTimeSkill(MycroftSkill):
    """
        Skill to handle mycroft speech client listener sleeping and
        awakening.
    """
    def initialize(self):
        self.sleeping = False
        self.old_brightness = 30
        self.add_event('mycroft.awoken', self.handle_awoken)

    @intent_handler(IntentBuilder("NapTimeIntent").require("SleepCommand"))
    def handle_go_to_sleep(self, message):
        """
            Sends a message to the speech client setting the listener in a
            sleep mode.
        """
        self.speak_dialog("going.to.sleep")
        self.emitter.emit(Message('recognizer_loop:sleep'))
        self.sleeping = True
        wait_while_speaking()
        time.sleep(2)
        wait_while_speaking()
        self.enclosure.eyes_narrow()

        # Dim and look downward to 'go to sleep'
        # TODO: Get current brightness from somewhere
        self.old_brightness = 30
        for i in range (0, (self.old_brightness-10)/2):
            self.enclosure.eyes_brightness(self.old_brightness - i*2)
            time.sleep(0.1)
        time.sleep(0.5)  # gives the brightness command time to finish
        self.enclosure.eyes_look("d")
        if self.config_core.get("enclosure").get("platform", "unknown") != "unknown":
            self.emitter.emit(Message('mycroft.volume.mute',
                                      data={"speak_message": False}))


    def handle_awoken(self, message):
        """
            Handler for the mycroft.awoken message (sent when the listener
            hears 'Hey Mycroft, Wake Up')
        """
        # Mild animation to come out of sleep from voice command
        # pop open eyes and wait a sec
        self.enclosure.eyes_reset()
        time.sleep(1)
        # brighten up and blink
        self.enclosure.eyes_brightness(15)
        self.enclosure.eyes_blink('b')
        time.sleep(1)
        # brighten the rest of the way and annouce "I'm awake"
        self.enclosure.eyes_brightness(self.old_brightness)
        self.speak_dialog("i.am.awake")
        self.awaken()

        wait_while_speaking()

    def awaken(self):
        if self.config_core.get("enclosure").get("platform", "unknown") != "unknown":
            self.emitter.emit(Message('mycroft.volume.unmute',
                                      data={"speak_message": False}))
        self.sleeping = False

    def stop(self):
        # Wake it up quietly when the button is pressed
        if self.sleeping:
            # brighten eyes slowly
            self.enclosure.eyes_reset()
            for i in range (0, (self.old_brightness-10)/2):
                self.enclosure.eyes_brightness(10 + i*2)
                time.sleep(0.1)
            # And blink
            self.enclosure.eyes_blink('b')
            self.emitter.emit(Message('recognizer_loop:wake_up'))
            self.awaken()
            return True
        else:
            return False


def create_skill():
    return NapTimeSkill()
