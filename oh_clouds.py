#!/usr/bin/env python3
"""
Figures the best temperature for redshift using camera.
"""

import argparse
import cv2
import logging
import subprocess

CAMERA_ID = 0
MIN_TEMPERATURE = 2000
MAX_TEMPERATURE = 6500

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def run(*cmd):
    logger.info('Executing: %s', ' '.join(cmd))
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        out, err = p.communicate()
        if err:
            logger.warning('Non-empty stderr "%s": %s', ' '.join(cmd), err)
        if p.returncode != 0:
            raise RuntimeError('Non-zero exit code "{}": {}'.format(' '.join(cmd), p.returncode))
        return out.decode('utf-8').strip()


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--camera', default=CAMERA_ID, type=int,
        help='camera ID')

    parser.add_argument(
        '--min-temperature', default=MIN_TEMPERATURE, type=int,
        help='minimum temperature value')

    parser.add_argument(
        '--max-temperature', default=MAX_TEMPERATURE, type=int,
        help='maximum temperature value')

    parser.add_argument(
        '--redshift', default='redshift',
        help='path to redshift executable')

    parser.add_argument(
        '--print-only', action='store_true',
        help='print temperature value, omit running redshift')

    parser.add_argument(
        '--reset', action='store_true',
        help='resets temperature')

    return parser.parse_args()


def main():
    args = parse_args()

    if args.reset:
        temperature = args.max_temperature
    else:
        capture = cv2.VideoCapture(args.camera)
        ret, img = capture.read()

        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pixel = img.mean()
        logger.info('Pixel mean: %s', int(pixel))
        value = min(1, pixel / 255 * 2)
        logger.info('Value: %s%%', int(100 * value))

        temperature = max(args.min_temperature, int(value * args.max_temperature))

    if args.print_only:
        print(temperature)
    else:
        logger.info('Temperature: %s', temperature)
        run(args.redshift, '-P', '-O', str(temperature))


if __name__ == "__main__":
    main()
