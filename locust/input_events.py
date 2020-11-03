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


class KeyPoller:
    def __enter__(self):
        if os.name == "nt":
            self.read_handle = GetStdHandle(STD_INPUT_HANDLE)
            self.read_handle.SetConsoleMode(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT)

            self.cur_event_length = 0
            self.cur_keys_length = 0

            self.captured_chars = []
        else:
            self.stdin = sys.stdin.fileno()
            self.tattr = termios.tcgetattr(self.stdin)
            tty.setcbreak(self.stdin, termios.TCSANOW)

        return self

    def __exit__(self, type, value, traceback):
        if not os.name == "nt":
            termios.tcsetattr(self.stdin, termios.TCSANOW, self.tattr)

    def poll(self):
        if os.name == "nt":
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
        else:
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            if not dr == []:
                return sys.stdin.read(1)
            return None


def input_listener(key_to_func_map):
    def input_listener_func():
        with KeyPoller() as poller:
            map = key_to_func_map
            while True:
                input = poller.poll()
                if input is not None:
                    logging.debug(f"Input key: {input}")
                    for key in map:
                        if input == key:
                            map[key]()
                else:
                    gevent.sleep(0.2)

    return input_listener_func
