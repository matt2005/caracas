#!/usr/bin/env python2.7
# coding: utf-8

SOCK = "tcp://localhost:9080"

import curses
import zmq
import syslog

EVENT_ZEROMQ = 0
EVENT_FUNCTION = 1
EVENT_QUIT = 2

COLOR_ON = 1
COLOR_OFF = 2
COLOR_SINGLE = 3

BUTTONS = [
    [False, ord('4'),           '4', 'Rotary left',     EVENT_ZEROMQ, 'ROTARY LEFT', None],
    [False, ord('5'),           '5', 'Rotary right',    EVENT_ZEROMQ, 'ROTARY RIGHT', None],
    [False, ord('6'),           '6', 'Rotary click',    EVENT_ZEROMQ, 'ROTARY PRESS', 'ROTARY DEPRESS'],
    [False, curses.KEY_LEFT,    'Left', 'Volume down',  EVENT_ZEROMQ, 'VOLUME DOWN PRESS', 'VOLUME DOWN DEPRESS'],
    [False, curses.KEY_RIGHT,   'Right', 'Volume up',   EVENT_ZEROMQ, 'VOLUME UP PRESS', 'VOLUME UP DEPRESS'],
    [False, curses.KEY_UP,      'Up', 'Arrow up',       EVENT_ZEROMQ, 'ARROW UP PRESS', 'ARROW UP DEPRESS'],
    [False, curses.KEY_DOWN,    'Down', 'Arrow down',   EVENT_ZEROMQ, 'ARROW DOWN PRESS', 'ARROW DOWN DEPRESS'],
    [True, ord('p'),            'P', 'Power',           EVENT_ZEROMQ, 'POWER ON', 'POWER OFF'],
    [False, ord(' '),           'Spacebar', 'Mode',     EVENT_ZEROMQ, 'MODE PRESS', 'MODE DEPRESS'],
    [True, ord('b'),            'B', 'Battery',         EVENT_ZEROMQ, 'BATTERY FULL', 'BATTERY CHARGING'],
    [False, ord('q'),           'Q', 'Quit',            EVENT_QUIT, None, None],
]

socket = None


def draw(stdscr):
    y = 0
    x = 0
    count = 0
    for arr in BUTTONS:
        if count > 0 and count % 5 == 0:
            y += 8
            x = 0
        count += 1
        stdscr.addstr(y, x, arr[3])
        if arr[6] == None:
            stdscr.addstr(y + 2, x, 'SINGLE', curses.color_pair(COLOR_SINGLE) | curses.A_BOLD)
        elif arr[0]:
            stdscr.addstr(y + 2, x, ' ON  ', curses.color_pair(COLOR_ON) | curses.A_BOLD)
        else:
            stdscr.addstr(y + 2, x, ' OFF ', curses.color_pair(COLOR_OFF) | curses.A_BOLD)
        stdscr.addstr(y + 4, x, 'Key: %s' % arr[2])
        x = x + max(len(arr[2])+5, len(arr[3])) + 3
    stdscr.refresh()

def match_input(c):
    for arr in BUTTONS:
        if c == arr[1]:
            return arr
    return None

def main(stdscr):
    curses.init_pair(COLOR_OFF, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(COLOR_ON, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(COLOR_SINGLE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    stdscr.clear()
    while True:
        draw(stdscr)
        c = stdscr.getch()
        arr = match_input(c)
        if not arr:
            continue
        if arr[4] == EVENT_QUIT:
            break
        elif arr[4] == EVENT_ZEROMQ:
            if arr[6] == None:
                data = arr[5]
            else:
                arr[0] = not arr[0]
                if arr[0]:
                    data = arr[5]
                else:
                    data = arr[6]
            syslog.syslog("Submitting event: %s" % data)
            socket.send_string(data)


if __name__ == '__main__':
    syslog.openlog('eventgen', syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog("Setting up ZeroMQ socket...")
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect(SOCK)
    syslog.syslog("Publishing events to %s" % SOCK)
    curses.wrapper(main)
