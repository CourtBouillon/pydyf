"""
Test suite for pydyf.

This module adds a PNG export based on GhostScript, that is released under
AGPL. As "the end user has the ability to opt out of installing the AGPL
version of [Ghostscript] during the install process", and with explicit
aggreement from Artifex, it is OK to distribute this code under BSD.

See https://www.ghostscript.com/license.html.

"""

import io
import os
from pathlib import Path
from subprocess import PIPE, run

from PIL import Image

PIXELS_BY_CHAR = dict(
    _=(255, 255, 255),  # white
    R=(255, 0, 0),  # red
    B=(0, 0, 255),  # blue
    G=(0, 255, 0),  # lime green
    K=(0, 0, 0),  # black
    z=None,  # any color
)


def assert_pixels(document, reference_pixels):
    """Test that the rendered document matches the reference pixels."""

    # Transform the PDF document into a list of RGB tuples
    pdf = io.BytesIO()
    document.write(pdf)
    command = [
        'gs', '-q', '-dNOPAUSE', '-dSAFER', '-sDEVICE=png16m',
        '-r576', '-dDownScaleFactor=8', '-sOutputFile=-', '-']
    png = run(command, input=pdf.getvalue(), stdout=PIPE).stdout
    image = Image.open(io.BytesIO(png))
    pixels = image.getdata()

    # Transform reference drawings into a list of RGB tuples
    lines = tuple(
        line.strip() for line in reference_pixels.splitlines() if line.strip())
    assert len({len(line) for line in lines}) == 1, (
        'The lines of reference pixels don’t have the same length')
    width, height = len(lines[0]), len(lines)
    assert (width, height) == image.size, (
        f'Reference size is {width}×{height}, '
        f'output size is {image.width}×{image.height}')
    reference_pixels = tuple(
        PIXELS_BY_CHAR[char] for line in lines for char in line)

    # Compare pixels
    if pixels != reference_pixels:  # pragma: no cover
        for i, (value, reference) in enumerate(zip(pixels, reference_pixels)):
            if reference is None:
                continue
            if any(value != reference
                   for value, reference in zip(value, reference)):
                name = os.environ.get('PYTEST_CURRENT_TEST')
                name = name.split(':')[-1].split(' ')[0]
                write_png(f'{name}', pixels, width, height)
                reference_pixels = [
                    pixel or (255, 255, 255) for pixel in reference_pixels]
                write_png(f'{name}-reference', reference_pixels, width, height)
                x, y = i % width, i // width
                assert 0, (
                    f'Pixel ({x}, {y}) in {name}: '
                    f'reference rgba{reference}, got rgba{value}')


def write_png(name, pixels, width, height):  # pragma: no cover
    """Take a pixel matrix and write a PNG file."""
    directory = Path(__file__).parent / 'results'
    directory.mkdir(exist_ok=True)
    image = Image.new('RGB', (width, height))
    image.putdata(pixels)
    image.save(directory / f'{name}.png')
