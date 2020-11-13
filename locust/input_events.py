import gevent
import logging
import os

if os.name == "nt":
    from win32api import STD_INPUT_HANDLE
    from win32console import (
        GetStdHandle,
        KEY_EVENT,
        ENABLE_ECHO_INPUT,
        ENABLE_LINE_INPUT,
        ENABLE_PROCESSED_INPUT,
    )
else:
    import sys
    import select
    import termios
    import tty


class UnixKeyPoller:
    def __init__(self):
        try:
            self.stdin = sys.stdin.fileno()
            self.tattr = termios.tcgetattr(self.stdin)
            tty.setcbreak(self.stdin, termios.TCSANOW)
        except termios.error:
            pass

    def cleanup(self):
        termios.tcsetattr(self.stdin, termios.TCSANOW, self.tattr)

    def poll(_self):
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if not dr == []:
            return sys.stdin.read(1)
        return None


class WindowsKeyPoller:
    def __init__(self):
        self.read_handle = GetStdHandle(STD_INPUT_HANDLE)
        self.read_handle.SetConsoleMode(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT)
        self.cur_event_length = 0
        self.cur_keys_length = 0
        self.captured_chars = []

    def cleanup(self):
        pass

    def poll(self):
        if self.captured_chars:
            return self.captured_chars.pop(0)

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
            return self.captured_chars.pop(0)
        else:
            return None


def get_poller():
    if os.name == "nt":
        return WindowsKeyPoller()
    else:
        return UnixKeyPoller()


def input_listener(key_to_func_map):
    poller = get_poller()

    def input_listener_func():
        try:
            while True:
                input = poller.poll()
                if input is not None:
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
