#!/usr/bin/env python
from __future__ import annotations

import logging
import queue
import threading
import time
from typing import Callable

logger = logging.getLogger(__name__)


class EventHandlerThread(threading.Thread):
    def __init__(self, service, event_handler: Callable, in_queue: queue.Queue) -> None:
        super().__init__()

        self._service = service
        self._in_queue: queue.Queue = in_queue
        self._event_handler = event_handler
        self.running = False

    def run(self) -> None:
        """ Primary thread function

        :return: None
        """
        self.running = True

        while self.running:
            event = None

            try:
                event = self._in_queue.get_nowait()
            except queue.Empty:
                pass

            if event:
                self._event_handler(event)

            time.sleep(0.01)

    def stop(self) -> None:
        """ Signals the thread that it needs to stop

        :return: None
        """
        self.running = False
