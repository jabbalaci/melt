"""
Some helper functions and constants.
"""

import os
import shlex
from subprocess import PIPE, STDOUT, Popen

import melt.config as cfg


CHAR_HORIZONTAL_LINE = '─'    # chr(9472)
CHAR_VERTICAL_LINE = '│'      # chr(9474)
CHAR_T_DOWN = '┬'             # chr(9516)
CHAR_T_UP = '┴'               # chr(9524)
CHAR_DOT = '●'                # chr(9679)

FRAME_COLOR = '\033[38;5;238m'
RED_COLOR = '\033[1;31m'
NO_COLOR = '\033[0m'

THREE_RED_DOTS = "{c}{d}{d}{d}{nc}".format(
    c=RED_COLOR,
    d=CHAR_DOT,
    nc=NO_COLOR
)


def get_simple_cmd_output(cmd: str, stderr=STDOUT) -> str:
    """
    Execute a simple external command and get its output.

    The command contains no pipes.
    """
    args = shlex.split(cmd)
    popen = Popen(args, stdout=PIPE, stderr=stderr)
    #
    return popen.communicate()[0].decode("utf8")


def get_terminal_width(half=False, panel: int = cfg.LEFT_SIDE) -> int:
    """
    Get the width of the terminal.

    It can also calculate the width of a panel. In the middle of
    the screen, there is a vertical bar between the panels.
    When we print in the right panel, we must leave the last column
    empty for the newline character.
    """
    full_width = int(get_simple_cmd_output("tput cols"))
    full_width_without_center_bar = full_width - 1
    left_panel_width = full_width_without_center_bar // 2
    # ... minus center bar minus newline:
    right_panel_width_without_newline = full_width - left_panel_width - 1 - 1

    if not half:
        return full_width    # complete length of a row in the terminal
    else:
        # if we take just half of the screen, then the left and right sides are in a frame
        if panel == cfg.LEFT_SIDE:
            return left_panel_width
        else:    # right side
            return right_panel_width_without_newline


def which(program):
    """
    Equivalent of the which command.

    source: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.split(program)[0]
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
