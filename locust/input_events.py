from __future__ import annotations

import collections
import logging
import os
import sys
from collections.abc import Callable

import gevent

if os.name == "nt":
    import pywintypes
    from win32api import STD_INPUT_HANDLE
    from win32console import (
        ENABLE_ECHO_INPUT,
        ENABLE_LINE_INPUT,
        ENABLE_PROCESSED_INPUT,
        KEY_EVENT,
        GetStdHandle,
    )
else:
    import select
    import termios
    import tty


class InitError(Exception):
    pass


class UnixKeyPoller:
    def __init__(self):
        if sys.stdin.isatty():
            self.stdin = sys.stdin.fileno()
            self.tattr = termios.tcgetattr(self.stdin)
            tty.setcbreak(self.stdin, termios.TCSANOW)
        else:
            raise InitError("Terminal was not a tty. Keyboard input disabled")

    def cleanup(self):
        termios.tcsetattr(self.stdin, termios.TCSANOW, self.tattr)

    def poll(_self):
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if not dr == []:
            return sys.stdin.read(1)
        return None


class WindowsKeyPoller:
    def __init__(self):
        if sys.stdin.isatty():
            try:
                self.read_handle = GetStdHandle(STD_INPUT_HANDLE)
                self.read_handle.SetConsoleMode(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT)
                self.cur_event_length = 0
                self.cur_keys_length = 0
                self.captured_chars = collections.deque()
            except pywintypes.error:
                raise InitError("Terminal says its a tty but we couldn't enable line input. Keyboard input disabled.")
        else:
            raise InitError("Terminal was not a tty. Keyboard input disabled")

    def cleanup(self):
        pass

    def poll(self):
        if self.captured_chars:
            return self.captured_chars.popleft()

        events_peek = self.read_handle.PeekConsoleInput(10000)

        if not events_peek:
            return None

        if not len(events_peek) == self.cur_event_length:
            for cur_event in events_peek[self.cur_event_length :]:
                if cur_event.EventType == KEY_EVENT:
                    if ord(cur_event.Char) and cur_event.KeyDown:
                        cur_char = str(cur_event.Char)
                        self.captured_chars.append(cur_char)

            self.cur_event_length = len(events_peek)

        if self.captured_chars:
            return self.captured_chars.popleft()
        else:
            return None


def get_poller():
    if os.name == "nt":
        return WindowsKeyPoller()
    else:
        return UnixKeyPoller()


def input_listener(key_to_func_map: dict[str, Callable]):
    def input_listener_func():
        try:
            poller = get_poller()
        except InitError as e:
            logging.debug(e)
            return

        try:
            while True:
                if input := poller.poll():
                    for key in key_to_func_map:
                        if input == key:
                            key_to_func_map[key]()
                else:
                    gevent.sleep(0.2)
        except Exception as e:
            logging.warning(f"Exception in keyboard input poller: {e}")
        finally:
            poller.cleanup()

    return input_listener_func
