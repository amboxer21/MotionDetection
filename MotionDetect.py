#!/usr/bin/env python

'''This is a video motion detector.

This uses about 5% CPU running with continuous motion detection on
a i5-3320M 2.6GHz with 16 GB RAM under no other load.

AUTHOR

    Noah Spurrier <noah@noah.org>

LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2014, Noah Spurrier
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

VERSION

    Version 2
'''

import cv2
import sys
import time

# The two main parameters that affect movement detection sensitivity
# are BLUR_SIZE and NOISE_CUTOFF. Both have little direct effect on
# CPU usage. In theory a smaller BLUR_SIZE should use less CPU, but
# for the range of values that are effective the difference is
# negligible. The default values are effective with on most light
# conditions with the cameras I have tested. At these levels the
# detectory can easily trigger on eye blinks, yet not trigger if the
# subject remains still without blinking. These levels will likely be
# useless outdoors.
BLUR_SIZE = 3
NOISE_CUTOFF = 12
# Ah, but the third main parameter that affects movement detection
# sensitivity is the time between frames. I like about 10 frames per
# second. Even 4 FPS is fine.
#FRAMES_PER_SECOND = 10

cam = cv2.VideoCapture(0)
# 320*240 = 76800 pixels
#cam.set(3, 320)
#cam.set(4, 240)
# 640*480 = 307200 pixels
cam.set(3,640)
cam.set(4,480)

window_name = "delta view"
#cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
window_name_now = "now view"
cv2.namedWindow(window_name_now, cv2.WINDOW_AUTOSIZE)

# Stabilize the detector by letting the camera warm up and
# seeding the first frames.
frame_now = cam.read()[1]
frame_now = cam.read()[1]
frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
frame_now = cv2.blur(frame_now, (BLUR_SIZE, BLUR_SIZE))
frame_prior = frame_now

delta_count_last = 1
while True:
    frame_delta = cv2.absdiff(frame_prior, frame_now)
    frame_delta = cv2.threshold(frame_delta, NOISE_CUTOFF, 255, 3)[1]
    delta_count = cv2.countNonZero(frame_delta)
    #if delta_count > 5:
        #sys.stdout.write("Moving\n")
        #sys.stdout.write("delta_count %s\n" + str(delta_count))

    # Visual detection statistics output.
    # Normalize improves brightness and contrast.
    # Mirror view makes self display more intuitive.
    cv2.normalize(frame_delta, frame_delta, 0, 255, cv2.NORM_MINMAX)
    frame_delta = cv2.flip(frame_delta, 1)
    cv2.putText(frame_delta, "DELTA: %d" % (delta_count),
            (5, 15), cv2.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255))
    cv2.imshow(window_name, frame_delta)

    #frame_delta = cv2.threshold(frame_delta, 92, 255, 0)[1]
    dst = cv2.flip(frame_now, 1)
    dst = cv2.addWeighted(dst,1.0, frame_delta,0.9,0)
    cv2.imshow(window_name_now, dst)

    # Stdout output.
    # Only output when there is new movement or when movement stops.
    # Time codes are in epoch time format.
    #if (delta_count_last == 0 and delta_count != 0):
    if(delta_count > 500):
        sys.stdout.write("MOVEMENT %f\n" % time.time())
        sys.stdout.flush()
    #elif delta_count_last != 0 and delta_count == 0:
        #sys.stdout.write("STILL    %f\n" % time.time())
        #sys.stdout.flush()
    #delta_count_last = delta_count

    # Advance the frames.
    frame_prior = frame_now
    frame_now = cam.read()[1]
    frame_now = cv2.cvtColor(frame_now, cv2.COLOR_RGB2GRAY)
    frame_now = cv2.blur(frame_now, (BLUR_SIZE, BLUR_SIZE))
    # Wait up to 10ms for a key press. Quit if the key is either ESC or 'q'.
    key = cv2.waitKey(10)
    if key == 0x1b or key == ord('q'):
        cv2.destroyWindow(window_name)
        break

#    # Morphology noise filters. They work, but really don't help much.
#    # A simple noise cutoff and blur is good enough.
#kernel = numpy.ones((5,5), numpy.uint8)
#    cv2.morphologyEx(frame_delta, cv2.MORPH_OPEN, kernel)
#    cv2.morphologyEx(frame_delta, cv2.MORPH_CLOSE, kernel)
#    # A bilateral filter also seems pointless.
#    #frame_now = cv2.bilateralFilter(frame_now,9,75,75)

# vim: set ft=python fileencoding=utf-8 sr et ts=4 sw=4 : See help 'modeline'
