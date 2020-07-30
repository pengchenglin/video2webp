from subprocess import Popen, PIPE
import shlex
import pathlib
import os
import sys


def run_command(command_line, shell=False):
    proc = Popen(shlex.split(command_line), stdout=PIPE, stderr=PIPE, shell=shell)
    out, err = proc.communicate()
    proc.stderr.close()
    proc.stdout.close()
    if proc.returncode:
        return False, err.decode('utf8')
    return True, out.decode('utf8')


def get_ffmpeg_binary():
    def try_command(cmd):
        try:
            run_command(cmd)
        except FileNotFoundError:
            return False
        else:
            return True

    cmds = [
        # "ffmpeg",
        # "./ffmpeg",
        # "{}/ffmpeg".format(str(pathlib.Path(__file__).parent.absolute()).replace("\\", "/"))

        "{}/ffmpeg".format(str(os.path.dirname(sys.executable)).replace("\\", "/"))
    ]

    for cmd in cmds:
        if try_command(cmd):
            print(cmd)
            return cmd
    raise SystemError("FFMPEG not found")


if __name__ == '__main__':
    print(get_ffmpeg_binary())