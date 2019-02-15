# Copyright (C) 2019 Iwan Timmer
# Copyright (C) 2017 Google Inc.
# SPDX-License-Identifier: Apache-2.0

import threading

from google.assistant.library.event import EventType

class Handler:

    def __init__(self, assistant, queue):
        self._assistant = assistant
        self._queue = queue
        self._plugins = []

    def add_plugin(self, plugin):
        self._plugins.append(plugin)

    def start(self):
        for event in self._queue:
            self._process_event(event);

    def start_converstation(self):
        self._assistant.start_conversation()

    def _process_event(self, event):
        for plugin in self._plugins:
            plugin.process_event(event)
