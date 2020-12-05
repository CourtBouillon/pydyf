"""
Test suite for pydyf

This module adds a PNG export based on GhostScript. As GhostScript is released
under AGPL, the whole testing suite is released under AGPL.

"""

import io
import os
import shutil
from subprocess import PIPE, run

from PIL import Image

PIXELS_BY_CHAR = dict(
    _=(255, 255, 255),  # white
    R=(255, 0, 0),  # red
    B=(0, 0, 255),  # blue
    G=(0, 255, 0),  # lime green
    K=(0, 0, 0),  # black
    z=None,
)


def document_to_png(document, target=None, resolution=72, antialiasing=1):
    output = io.BytesIO()
    document.write(output)
    # TODO: don’t crash if GhostScript can’t be found
    # TODO: fix that for Windows
    command = [
        'gs', '-q',
        '-sstdout=%%stderr' if os.name == 'nt' else '-sstdout=%stderr',
        '-dNOPAUSE', '-dSAFER', f'-dTextAlphaBits={antialiasing}',
        f'-dGraphicsAlphaBits={antialiasing}', '-sDEVICE=png16m',
        f'-r{resolution * 8}', '-dDownScaleFactor=8', '-sOutputFile=-', '-']
    command = run(command, input=output.getvalue(), stdout=PIPE)
    pngs = command.stdout
    magic_number = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'

    # TODO: use a different way to find PNG files in stream
    if pngs.count(magic_number) == 1:
        if target is None:
            return pngs
        png = io.BytesIO(pngs)
    else:
        images = []
        for i, png in enumerate(pngs[8:].split(magic_number)):
            images.append(Image.open(io.BytesIO(magic_number + png)))

        width = max(image.width for image in images)
        height = sum(image.height for image in images)
        output_image = Image.new('RGBA', (width, height))
        top = 0
        for image in images:
            output_image.paste(
                image, (int((width - image.width) / 2), top))
            top += image.height
        png = io.BytesIO()
        output_image.save(png, format='png')

    png.seek(0)

    if target is None:
        return png.read()

    if hasattr(target, 'write'):
        shutil.copyfileobj(png, target)
    else:
        with open(target, 'wb') as fd:
            shutil.copyfileobj(png, fd)


def parse_pixels(pixels, pixels_overrides=None):
    chars = dict(PIXELS_BY_CHAR, **(pixels_overrides or {}))
    lines = tuple(line.split('#')[0].strip() for line in pixels.splitlines())
    lines = tuple(line for line in lines if line)
    width, height = len(lines[0]), len(lines)
    pixels = tuple(chars[char] for line in lines for char in line)
    return pixels, width, height


def assert_pixels(document, reference_pixels):
    """Helper testing the size of the image and the pixels values."""
    png = document_to_png(document)
    reference_pixels, width, height = parse_pixels(reference_pixels)
    image = Image.open(io.BytesIO(png))
    assert (width, height) == image.size, (
        f'Reference size is {width}×{height}, '
        f'output size is {image.width}×{image.height}')
    pixels = image.getdata()
    assert_pixels_equal(width, height, pixels, reference_pixels)


def write_png(basename, pixels, width, height):  # pragma: no cover
    """Take a pixel matrix and write a PNG file."""
    directory = os.path.join(os.path.dirname(__file__), 'results')
    if not os.path.isdir(directory):
        os.mkdir(directory)
    filename = os.path.join(directory, basename + '.png')
    image = Image.new('RGB', (width, height))
    image.putdata(pixels)
    image.save(filename)


def assert_pixels_equal(width, height, raw, reference_raw, tolerance=0):
    """Take 2 matrices of pixels and assert that they are the same."""
    if raw != reference_raw:  # pragma: no cover
        for i, (value, reference) in enumerate(zip(raw, reference_raw)):
            if reference is None:
                continue
            if any(abs(value - reference) > tolerance
                   for value, reference in zip(value, reference)):
                name = os.environ.get('PYTEST_CURRENT_TEST')
                name = name.split(':')[-1].split(' ')[0]
                write_png(name, raw, width, height)
                reference_raw = [
                    pixel or (255, 255, 255) for pixel in reference_raw]
                write_png(name + '.reference', reference_raw, width, height)
                x = i // width
                y = i % width
                assert 0, (
                    f'Pixel ({x}, {y}) in {name}: '
                    f'reference rgba{reference}, got rgba{value}')
