#!/usr/bin/env python3

"""
melt - a visual cat-like file viewer with syntax highlighting
       supporting 2-file views

The syntax highlighting is done with the bat tool
that you need to install first (see https://github.com/sharkdp/bat).


Author: Laszlo Szathmary, alias Jabba Laci, 2019
E-mail: jabba.laci@gmail.com
GitHub: https://github.com/jabbalaci/melt
"""

import atexit
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import melt.config as cfg
from melt import docs, helper

OFFSET = 5    # space for line numbers


#####################
## class PlainFile ##
#####################

class PlainFile:
    """
    Plain input file without any syntax highlighting.
    """

    def __init__(self, fname: str, tmp_dir_path: str, panel: int) -> None:
        self.fname = fname    # can be a relative or an absolute path too
        self.fname_only = Path(fname).name    # just the name, no path to it
        self.tmp_dir_path = tmp_dir_path
        self.idx_of_too_long_lines: Set[int] = set()
        # this is the maximal length of a line to fit in a frame (OFFSET is for the line numbers):
        self.line_length_limit = helper.get_terminal_width(half=True, panel=panel) - OFFSET
        #
        # self.tmp_file_path is created later

    def read(self) -> None:
        with open(self.fname) as f:
            self.lines = f.readlines()
        #
        self.lines = self.clean_lines(self.lines)
        #
        for idx, line in enumerate(self.lines):
            if len(line) > self.line_length_limit:
                line = line[:self.line_length_limit-3]    # truncate and leave space for the 3 dots
                self.lines[idx] = line
                self.idx_of_too_long_lines.add(idx)

    def clean_lines(self, lines: List[str]) -> List[str]:
        lines = [line.rstrip().expandtabs() for line in lines]
        while (len(lines) > 0) and (lines[-1] == ""):
            lines.pop()
        #
        return lines

    def max_width(self, offset: int = 0) -> int:
        return max(len(line) for line in self.lines) + offset

    def get_number_of_lines(self) -> int:
        return len(self.lines)

    def add_extra_lines(self, goal: int) -> None:
        for _ in range(goal - self.get_number_of_lines()):
            self.lines.append("")

    def save_as_tmp(self) -> None:
        tmp = tempfile.NamedTemporaryFile(dir=self.tmp_dir_path).name
        fname = f"{tmp}_{self.fname_only}"
        self.tmp_file_path = fname
        # print(self.tmp_file_path)
        with open(fname, "w") as f:
            for line in self.lines:
                print(line, file=f)


#######################
## class ColoredFile ##
#######################

class ColoredFile:
    """
    Syntax highlighted version of the input file.
    """

    def __init__(self, plain_file: PlainFile, options: Dict[str, Any]) -> None:
        self.pf = plain_file
        self.light = bool(options.get("light"))    # True or False
        # self.fname is set later

    def save_file(self) -> None:
        tmp = tempfile.NamedTemporaryFile(dir=self.pf.tmp_dir_path).name
        fname = f"{tmp}_{self.pf.fname_only}"
        self.fname = fname
        #
        cmd = "{bat} --color=always --style numbers {light} {fn}".format(
            bat=cfg.BAT,
            light=f"--theme={cfg.LIGHT_THEME}" if self.light else "",
            fn=self.pf.tmp_file_path
        )
        # print("#", cmd)
        self.lines = helper.get_simple_cmd_output(cmd).splitlines()
        with open(self.fname, "w") as f:
            for line in self.lines:
                print(line, file=f)

    def pad_lines_on_right(self) -> None:
        assert len(self.pf.lines) == len(self.lines)
        #
        # width = helper.get_terminal_width(half=True)
        width = self.pf.line_length_limit + OFFSET    # width of the panel
        for idx in range(len(self.pf.lines)):
            if idx in self.pf.idx_of_too_long_lines:
                self.lines[idx] += helper.THREE_RED_DOTS
            else:
                plain_line = self.pf.lines[idx]
                length = len(plain_line) + OFFSET
                spaces = " " * (width - length)
                self.lines[idx] += spaces

#############################################################################

def merge_colored_files(cf1: ColoredFile, cf2: ColoredFile) -> None:
    """
    Merge the colored versions of the files and place them side by side.
    """
    assert len(cf1.lines) == len(cf2.lines)
    #
    width = helper.get_terminal_width()
    line = [helper.CHAR_HORIZONTAL_LINE] * width
    idx = helper.get_terminal_width(half=True)
    line[idx] = helper.CHAR_T_DOWN
    hr = "{c}{line}{nc}".format(c=helper.FRAME_COLOR,
                                line="".join(line),
                                nc=helper.NO_COLOR)
    sys.stdout.write(hr)
    #
    for l1, l2 in zip(cf1.lines, cf2.lines):
        sys.stdout.write(l1)
        sys.stdout.write("{c}{char}{nc}".format(c=helper.FRAME_COLOR,
                                                char=helper.CHAR_VERTICAL_LINE,
                                                nc=helper.NO_COLOR))
        print(l2)
    #
    line[idx] = helper.CHAR_T_UP
    hr = "{c}{line}{nc}".format(c=helper.FRAME_COLOR,
                                line="".join(line),
                                nc=helper.NO_COLOR)
    print(hr)


def make_equal_long(pf1: PlainFile, pf2: PlainFile) -> None:
    """
    The two files must have the same number of lines.

    If one of them is shorter, then fill it up with
    blank lines.
    """
    maxi = max([pf1.get_number_of_lines(), pf2.get_number_of_lines()])
    pf1.add_extra_lines(maxi)
    pf2.add_extra_lines(maxi)


def check_command_line_args(argv: List[str]) -> Tuple[str, str, Dict[str, Any]]:
    """
    Treat the command-line arguments.
    """
    args = argv[1:]
    options: Dict[str, Any] = {}

    if "--light" in args:
        options['light'] = True
        args.remove("--light")

    if (len(args) == 0) or ("-h" in args) or ("--help" in args):
        docs.show_help()
        sys.exit(0)

    if len(args) != 2:
        print("Error: provide two input files / use valid options", file=sys.stderr)
        sys.exit(1)
    # else
    fname1, fname2 = args
    return fname1, fname2, options

##############################################################################

def check_if_bat_exists() -> None:
    """
    The program requires bat for the syntax highlighting.
    """
    if not helper.which(cfg.BAT):
        print("Error: bat not found.", file=sys.stderr)
        print("Tip: visit https://github.com/sharkdp/bat and install it.", file=sys.stderr)
        sys.exit(1)


def main(argv: List[str]) -> None:
    """
    Controller.
    """
    check_if_bat_exists()
    # if bat is available:

    fname1, fname2, options = check_command_line_args(argv)

    tmp_dir_path = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, tmp_dir_path)

    pf1 = PlainFile(fname1, tmp_dir_path, cfg.LEFT_SIDE)
    pf1.read()
    pf2 = PlainFile(fname2, tmp_dir_path, cfg.RIGHT_SIDE)
    pf2.read()
    make_equal_long(pf1, pf2)

    pf1.save_as_tmp()
    pf2.save_as_tmp()

    cf1 = ColoredFile(pf1, options)
    cf1.save_file()

    cf2 = ColoredFile(pf2, options)
    cf2.save_file()

    cf1.pad_lines_on_right()
    cf2.pad_lines_on_right()

    merge_colored_files(cf1, cf2)

##############################################################################

if __name__ == "__main__":
    main(sys.argv)
