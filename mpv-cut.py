#!/usr/bin/env python3
# For mpv.
import os, sys, glob, fire
from pathlib import Path
from subprocess import Popen, PIPE
sys.path.append(os.path.expanduser('~/work'))
from xattr import xattr

def url(p):
    try:
        return xattr(p)['user.xdg.referrer.url'].decode('ascii')
    except:
        return ''


def main():
    f = os.popen('mpv-np').read().strip()
    u = url(f)
    dur = float(os.popen(f'''ffprobe -i "{f}" -show_format -v quiet | sed -n 's/duration=//p' ''').read().strip())
    pos =float(os.popen('qdbus org.mpris.MediaPlayer2.mpv  /org/mpris/MediaPlayer2  org.mpris.MediaPlayer2.Player.Position').read().strip())
    l =float(os.popen('qdbus org.mpris.MediaPlayer2.mpv  /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.Metadata|grep length').read().strip().split(':')[-1])
    s = l/pos
    sec = int(dur/s)
    bn = os.path.basename(f)
    os.system(f'notify-send -t 500 "{sec}s/{dur}s {bn}"')
    os.system(f'''ffmpeg -y -i "{f}" -ss {sec} -vcodec copy -acodec copy "/tmp/{bn}" && cp "/tmp/{bn}" "{f}"''')
    xattr(f)['user.xdg.referrer.url'] = u.encode('ascii')

    ''' main '''
    pass

if __name__ == '__main__':
    fire.Fire(main)
