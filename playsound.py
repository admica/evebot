#!/usr/bin/python -OOtt
# -*- coding: utf-8 -*-

import sys

CHUNK = 512

try:
    if len(sys.argv) < 2:
        print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
        sys.exit(-1)

    import wave
    wf = wave.open(sys.argv[1], 'rb')

    import pyaudio
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    from time import sleep
    sleep(0.33)

    stream.stop_stream()
    stream.close()

    p.terminate()
    sys.exit(0)

except:
    sys.exit(1)
