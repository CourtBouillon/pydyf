import io
import re
from subprocess import PIPE, run

import pytest
from PIL import Image

import pydyf

from . import assert_pixels


@pytest.mark.parametrize('compress', [False, True])
def test_fill(compress):
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.fill()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __________
        __________
    ''', compress)


def test_stroke():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_line_width(2)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        _KKKKKKK__
        _KKKKKKK__
        _KK___KK__
        _KK___KK__
        _KK___KK__
        _KK___KK__
        _KKKKKKK__
        _KKKKKKK__
        __________
    ''')


def test_line_to():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 2)
    draw.set_line_width(2)
    draw.line_to(2, 5)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        __________
        _KK_______
        _KK_______
        _KK_______
        __________
        __________
    ''')


def test_line_cap():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 2)
    draw.set_line_width(2)
    draw.set_line_cap(2)
    draw.line_to(2, 5)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        _KK_______
        _KK_______
        _KK_______
        _KK_______
        _KK_______
        __________
    ''')


def test_line_join():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(3, 1)
    draw.set_line_width(4)
    draw.set_line_join(2)
    draw.line_to(3, 5)
    draw.line_to(7, 5)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __zzKKK___
        _zzKKKK___
        _zKKKKK___
        _KKKKKK___
        _KKKK_____
        _KKKK_____
        __________
    ''')


def test_line_miter_limit():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(3, 1)
    draw.set_line_width(4)
    draw.set_miter_limit(2)
    draw.line_to(3, 5)
    draw.line_to(3.1, 1)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        _zzzzz____
        _KKKKz____
        _KKKKz____
        _KKKKz____
        _KKKKz____
        _zzzzz____
    ''')


def test_set_color_rgb_stroke():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_line_width(2)
    draw.set_color_rgb(0, 0, 255, stroke=True)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        _BBBBBBB__
        _BBBBBBB__
        _BB___BB__
        _BB___BB__
        _BB___BB__
        _BB___BB__
        _BBBBBBB__
        _BBBBBBB__
        __________
    ''')


def test_set_color_rgb_fill():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_color_rgb(255, 0, 0)
    draw.fill()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __RRRRR___
        __RRRRR___
        __RRRRR___
        __RRRRR___
        __RRRRR___
        __RRRRR___
        __________
        __________
    ''')


def test_set_color_special_stroke():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_line_width(2)
    draw.set_color_space('DeviceGray')
    draw.set_color_special(0, stroke=True)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        _KKKKKKK__
        _KKKKKKK__
        _KK___KK__
        _KK___KK__
        _KK___KK__
        _KK___KK__
        _KKKKKKK__
        _KKKKKKK__
        __________
    ''')


def test_set_color_special_fill():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_color_space('DeviceGray')
    draw.set_color_special(0)
    draw.fill()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __________
        __________
    ''')


def test_set_dash():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 2)
    draw.set_line_width(2)
    draw.line_to(2, 6)
    draw.set_dash([2, 1], 0)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        _KK_______
        __________
        _KK_______
        _KK_______
        __________
        __________
    ''')


def test_curve_to():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 5)
    draw.set_line_width(2)
    draw.curve_to(2, 5, 3, 5, 5, 5)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        __KKK_____
        __KKK_____
        __________
        __________
        __________
        __________
    ''')


def test_curve_start_to():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 5)
    draw.set_line_width(2)
    draw.curve_start_to(3, 5, 5, 5)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        __KKK_____
        __KKK_____
        __________
        __________
        __________
        __________
    ''')


def test_curve_end_to():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 5)
    draw.set_line_width(2)
    draw.curve_end_to(3, 5, 5, 5)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        __KKK_____
        __KKK_____
        __________
        __________
        __________
        __________
    ''')


def test_set_matrix():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.set_matrix(1, 0, 0, 1, 1, 1)
    draw.move_to(2, 2)
    draw.set_line_width(2)
    draw.line_to(2, 5)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        __KK______
        __KK______
        __KK______
        __________
        __________
        __________
    ''')


def test_set_state():
    document = pydyf.PDF()

    graphic_state = pydyf.Dictionary({
        'Type': '/ExtGState',
        'LW': 2,
    })
    document.add_object(graphic_state)

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_state('GS')
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'ExtGState': pydyf.Dictionary({'GS': graphic_state.reference}),
        }),
    }))

    assert_pixels(document, '''
        __________
        _KKKKKKK__
        _KKKKKKK__
        _KK___KK__
        _KK___KK__
        _KK___KK__
        _KK___KK__
        _KKKKKKK__
        _KKKKKKK__
        __________
    ''')


def test_fill_and_stroke():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_line_width(2)
    draw.set_color_rgb(0, 0, 255, stroke=True)
    draw.fill_and_stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        _BBBBBBB__
        _BBBBBBB__
        _BBKKKBB__
        _BBKKKBB__
        _BBKKKBB__
        _BBKKKBB__
        _BBBBBBB__
        _BBBBBBB__
        __________
    ''')


def test_clip():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(3, 3, 5, 6)
    draw.rectangle(4, 3, 2, 6)
    draw.clip()
    draw.end()
    draw.move_to(0, 5)
    draw.line_to(10, 5)
    draw.set_color_rgb(255, 0, 0, stroke=True)
    draw.set_line_width(2)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        ___RRRRR__
        ___RRRRR__
        __________
        __________
        __________
        __________
    ''')


def test_clip_even_odd():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(3, 3, 5, 6)
    draw.rectangle(4, 3, 2, 6)
    draw.clip(even_odd=True)
    draw.end()
    draw.move_to(0, 5)
    draw.line_to(10, 5)
    draw.set_color_rgb(255, 0, 0, stroke=True)
    draw.set_line_width(2)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        ___R__RR__
        ___R__RR__
        __________
        __________
        __________
        __________
    ''')


def test_close():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 2)
    draw.line_to(2, 8)
    draw.line_to(7, 8)
    draw.line_to(7, 2)
    draw.close()
    draw.set_color_rgb(0, 0, 255, stroke=True)
    draw.set_line_width(2)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        _BBBBBBB__
        _BBBBBBB__
        _BB___BB__
        _BB___BB__
        _BB___BB__
        _BB___BB__
        _BBBBBBB__
        _BBBBBBB__
        __________
    ''')


def test_stroke_and_close():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 2)
    draw.line_to(2, 8)
    draw.line_to(7, 8)
    draw.line_to(7, 2)
    draw.set_color_rgb(0, 0, 255, stroke=True)
    draw.set_line_width(2)
    draw.stroke_and_close()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        _BBBBBBB__
        _BBBBBBB__
        _BB___BB__
        _BB___BB__
        _BB___BB__
        _BB___BB__
        _BBBBBBB__
        _BBBBBBB__
        __________
    ''')


def test_fill_stroke_and_close():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 2)
    draw.line_to(2, 8)
    draw.line_to(7, 8)
    draw.line_to(7, 2)
    draw.set_color_rgb(255, 0, 0)
    draw.set_color_rgb(0, 0, 255, stroke=True)
    draw.set_line_width(2)
    draw.fill_stroke_and_close()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        _BBBBBBB__
        _BBBBBBB__
        _BBRRRBB__
        _BBRRRBB__
        _BBRRRBB__
        _BBRRRBB__
        _BBBBBBB__
        _BBBBBBB__
        __________
    ''')


def test_push_pop_state():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.push_state()
    draw.rectangle(4, 4, 2, 2)
    draw.set_color_rgb(255, 0, 0)
    draw.pop_state()
    draw.fill()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __________
        __________
    ''')


def test_inline_image():
    document = pydyf.PDF()

    x, y, width, height = 1, 1, 2, 2
    image = Image.new('1', (width, height))
    image.putdata((0, 1, 1, 0))
    raw_data = image.tobytes()

    draw = pydyf.Stream()
    draw.push_state()
    draw.set_matrix(width, 0, 0, height, x, y)
    draw.inline_image(width, height, 'Gray', 1, raw_data)
    draw.pop_state()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 4, 4]),
        'Resources': pydyf.Dictionary({
            'ProcSet': pydyf.Array(['/PDF', '/ImageB', '/ImageC', '/ImageI']),
        }),
    }))

    assert_pixels(document, '''
        ____
        _K__
        __K_
        ____
    ''')


def test_pattern():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.push_state()
    draw.set_color_space('Pattern')
    draw.set_color_special('p0')
    draw.rectangle(0, 0, 10, 10)
    draw.fill()
    draw.pop_state()
    document.add_object(draw)

    x_object = pydyf.Stream(extra=pydyf.Dictionary({
        'Type': '/XObject',
        'Subtype': '/Form',
        'BBox': pydyf.Array((0, 0, 10, 10)),
        'Resources': pydyf.Dictionary({
            'Shading': pydyf.Dictionary({
                's0': pydyf.Dictionary({
                    'ShadingType': 2,
                    'ColorSpace': '/DeviceRGB',
                    'Domain': pydyf.Array((0, 1)),
                    'Coords': pydyf.Array((0, 5, 10, 5)),
                    'Function': pydyf.Dictionary({
                        'FunctionType': 3,
                        'Domain': pydyf.Array((0, 1)),
                        'Encode': pydyf.Array((0, 1, 0, 1, 0, 1)),
                        'Bounds': pydyf.Array((0.5, 0.5)),
                        'Functions': pydyf.Array((
                            pydyf.Dictionary({
                                'FunctionType': 2,
                                'Domain': pydyf.Array((0, 1)),
                                'C0': pydyf.Array((1, 1, 1)),
                                'C1': pydyf.Array((1, 1, 1)),
                                'N': 1,
                            }),
                            pydyf.Dictionary({
                                'FunctionType': 2,
                                'Domain': pydyf.Array((0, 1)),
                                'C0': pydyf.Array((1, 1, 1)),
                                'C1': pydyf.Array((1, 0, 0)),
                                'N': 1,
                            }),
                            pydyf.Dictionary({
                                'FunctionType': 2,
                                'Domain': pydyf.Array((0, 1)),
                                'C0': pydyf.Array((1, 0, 0)),
                                'C1': pydyf.Array((1, 0, 0)),
                                'N': 1,
                            }),
                        )),
                    }),
                }),
            }),
        }),
    }))
    x_object.paint_shading('s0')
    document.add_object(x_object)

    pattern = pydyf.Stream(extra=pydyf.Dictionary({
        'Type': '/Pattern',
        'PatternType': 1,
        'BBox': pydyf.Array((0, 0, 10, 10)),
        'XStep': 10,
        'YStep': 10,
        'TilingType': 1,
        'PaintType': 1,
        'Resources': pydyf.Dictionary({
            'XObject': pydyf.Dictionary({'x0': x_object.reference}),
        }),
    }))
    pattern.draw_x_object('x0')
    document.add_object(pattern)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'Pattern': pydyf.Dictionary({'p0': pattern.reference}),
        }),
    }))

    assert_pixels(document, '''
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
        ____zzRRRR
    ''')


def test_begin_end_marked_content():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.begin_marked_content('Artifact')
    draw.rectangle(2, 2, 5, 6)
    draw.fill()
    draw.end_marked_content()
    document.add_object(draw)

    pdf = io.BytesIO()
    document.write(pdf, version=b'2.0')
    pdf_bytes = pdf.getvalue()
    assert b'BMC' in pdf_bytes
    assert b'EMC' in pdf_bytes


def test_begin_end_marked_content_properties():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    property_list = pydyf.Dictionary({'MCID': 10})
    draw.begin_marked_content('Artifact', property_list)
    draw.rectangle(2, 2, 5, 6)
    draw.fill()
    draw.end_marked_content()
    document.add_object(draw)

    pdf = io.BytesIO()
    document.write(pdf, version=b'2.0')
    pdf_bytes = pdf.getvalue()
    assert b'BDC' in pdf_bytes
    assert b'/MCID' in pdf_bytes
    assert b'EMC' in pdf_bytes


def test_types():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2.0, '5', b'6')
    draw.set_line_width(2.3456)
    draw.fill()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __________
        __________
    ''')


def test_compress():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.fill()
    assert b'2 2 5 6' in draw.data

    draw = pydyf.Stream(compress=True)
    draw.rectangle(2, 2, 5, 6)
    draw.fill()
    assert b'2 2 5 6' not in draw.data
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert_pixels(document, '''
        __________
        __________
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __KKKKK___
        __________
        __________
    ''')


def test_text():
    document = pydyf.PDF()

    font = pydyf.Dictionary({
        'Type': '/Font',
        'Subtype': '/Type1',
        'Name': '/F1',
        'BaseFont': '/Helvetica',
        'Encoding': '/MacRomanEncoding',
    })
    document.add_object(font)

    draw = pydyf.Stream()
    draw.begin_text()
    draw.set_font_size('F1', 200)
    draw.set_text_matrix(1, 0, 0, 1, -20, 5)
    draw.show_text(pydyf.String('l'))
    draw.show_text(pydyf.String('É'))
    draw.end_text()

    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'ProcSet': pydyf.Array(['/PDF', '/Text']),
            'Font': pydyf.Dictionary({'F1': font.reference}),
        }),
    }))

    assert_pixels(document, '''
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        zzzzzzzzzz
        __________
        __________
        __________
        __________
    ''')


def test_text_string():
    document = pydyf.PDF()

    font = pydyf.Dictionary({
        'Type': '/Font',
        'Subtype': '/Type1',
        'Name': '/F1',
        'BaseFont': '/Helvetica',
        'Encoding': '/MacRomanEncoding',
    })
    document.add_object(font)

    draw = pydyf.Stream()
    draw.begin_text()
    draw.set_font_size('F1', 200)
    draw.set_text_matrix(1, 0, 0, 1, -20, 5)
    draw.show_text_string('l')
    draw.end_text()

    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'ProcSet': pydyf.Array(['/PDF', '/Text']),
            'Font': pydyf.Dictionary({'F1': font.reference}),
        }),
    }))

    assert_pixels(document, '''
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        zzzzzzzzzz
        __________
        __________
        __________
        __________
    ''')


def test_move_text_to():
    document = pydyf.PDF()

    font = pydyf.Dictionary({
        'Type': '/Font',
        'Subtype': '/Type1',
        'Name': '/F1',
        'BaseFont': '/Helvetica',
        'Encoding': '/MacRomanEncoding',
    })
    document.add_object(font)

    draw = pydyf.Stream()
    draw.begin_text()
    draw.set_font_size('F1', 200)
    draw.move_text_to(-20, 5)
    draw.show_text(pydyf.String('l'))
    draw.end_text()

    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'ProcSet': pydyf.Array(['/PDF', '/Text']),
            'Font': pydyf.Dictionary({'F1': font.reference}),
        }),
    }))

    assert_pixels(document, '''
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        KKKKKKKKKK
        zzzzzzzzzz
        __________
        __________
        __________
        __________
    ''')


def test_text_rise():
    document = pydyf.PDF()

    font = pydyf.Dictionary({
        'Type': '/Font',
        'Subtype': '/Type1',
        'Name': '/F1',
        'BaseFont': '/Helvetica',
        'Encoding': '/MacRomanEncoding',
    })
    document.add_object(font)

    draw = pydyf.Stream()
    draw.begin_text()
    draw.set_font_size('F1', 200)
    draw.set_text_matrix(1, 0, 0, 1, -20, 5)
    draw.set_text_rise(3)
    draw.show_text(pydyf.String('l'))
    draw.end_text()

    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'ProcSet': pydyf.Array(['/PDF', '/Text']),
            'Font': pydyf.Dictionary({'F1': font.reference}),
        }),
    }))

    assert_pixels(document, '''
        KKKKKKKKKK
        KKKKKKKKKK
        zzzzzzzzzz
        __________
        __________
        __________
        __________
        __________
        __________
        __________
    ''')


def test_text_rendering():
    document = pydyf.PDF()

    font = pydyf.Dictionary({
        'Type': '/Font',
        'Subtype': '/Type1',
        'Name': '/F1',
        'BaseFont': '/Helvetica',
        'Encoding': '/MacRomanEncoding',
    })
    document.add_object(font)

    draw = pydyf.Stream()
    draw.begin_text()
    draw.set_font_size('F1', 200)
    draw.set_text_matrix(1, 0, 0, 1, -20, 5)
    draw.set_text_rendering(3)
    draw.show_text(pydyf.String('l'))
    draw.end_text()

    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'ProcSet': pydyf.Array(['/PDF', '/Text']),
            'Font': pydyf.Dictionary({'F1': font.reference}),
        }),
    }))

    assert_pixels(document, '''
        __________
        __________
        __________
        __________
        __________
        __________
        __________
        __________
        __________
        __________
    ''')


@pytest.mark.parametrize('compress', [False, True])
def test_no_identifier(compress):
    document = pydyf.PDF()
    pdf = io.BytesIO()
    document.write(pdf, compress=compress, identifier=False)
    assert re.search(
        b'/ID \\[\\((?P<hash>[0-9a-f]{32})\\) \\((?P=hash)\\)\\]',
        pdf.getvalue()
    ) is None


@pytest.mark.parametrize('compress', [False, True])
def test_default_identifier(compress):
    document = pydyf.PDF()
    pdf = io.BytesIO()
    document.write(pdf, compress=compress, identifier=True)
    assert re.search(
        b'/ID \\[\\((?P<hash>[0-9a-f]{32})\\) \\((?P=hash)\\)\\]',
        pdf.getvalue()
    ) is not None


@pytest.mark.parametrize('compress', [False, True])
def test_custom_identifier(compress):
    document = pydyf.PDF()
    pdf = io.BytesIO()
    document.write(pdf, compress=compress, identifier=b'abc')
    assert re.search(
        b'/ID \\[\\(abc\\) \\(([0-9a-f]{32})\\)\\]',
        pdf.getvalue()
    ) is not None


@pytest.mark.parametrize('compress', [False, True])
def test_info(compress):
    document = pydyf.PDF()
    document.info['Producer'] = 'pydyf'
    pdf = io.BytesIO()
    document.write(pdf, compress=compress)
    pdf_bytes = pdf.getvalue()
    assert b'Info' in pdf_bytes
    if not compress:
        assert b'Producer' in pdf_bytes
        assert b'pydyf' in pdf_bytes


@pytest.mark.parametrize('compress', [False, True])
def test_no_info(compress):
    document = pydyf.PDF()
    pdf = io.BytesIO()
    document.write(pdf, compress=compress)
    assert b'Info' not in pdf.getvalue()


def test_page_references():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.rectangle(2, 2, 5, 6)
    draw.set_line_width(2)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert len(document.page_references) == 1

    draw = pydyf.Stream()
    draw.rectangle(1, 1, 2, 3)
    draw.fill()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))

    assert len(document.page_references) == 2


def test_version():
    document = pydyf.PDF()
    pdf = io.BytesIO()
    document.write(pdf, version=b'2.0')
    assert b'2.0' in pdf.getvalue()


@pytest.mark.parametrize(('string', 'data'), [
    ('abc', b'(abc)'),
    ('déf', b'<feff006400e90066>'),
    ('♡', b'<feff2661>'),
    ('\\abc', b'(\\\\abc)'),
    ('abc(', b'(abc\\()'),
    ('ab)c', b'(ab\\)c)'),
])
def test_string_encoding(string, data):
    assert pydyf.String(string).data == data


@pytest.mark.parametrize(('string', 'name'), [
    ('abc', b'/abc'),
    ('A;Name_With-Various***Characters?', b'/A;Name_With-Various***Characters?'),
    ('1.2', b'/1.2'),
    ('$$', b'/$$'),
    ('@pattern', b'/@pattern'),
    ('.notdef', b'/.notdef'),
    ('Lime Green', b'/Lime#20Green'),
    ('paired()parentheses', b'/paired#28#29parentheses'),
    ('The_Key_of_F#_Minor', b'/The_Key_of_F#23_Minor'),
])
def test_name_object(string, name):
    assert pydyf.name(string) == name


@pytest.mark.parametrize(('string', 'name'), [
    ('rate%off', b'/rate#25off'),
    ('%comment', b'/#25comment'),
    ('100%', b'/100#25'),
    ('%20', b'/#2520'),
    ('{name}', b'/#7bname#7d'),
    ('<>/[]()#%', b'/#3c#3e#2f#5b#5d#28#29#23#25'),
    ('é\t\n', b'/#c3#a9#09#0a'),
])
def test_name_delimiters(string, name):
    assert pydyf.name(string) == name


@pytest.mark.parametrize('string', ['\0', 'part\0name'])
def test_name_null_byte(string):
    with pytest.raises(ValueError, match='null'):
        pydyf.name(string)


@pytest.mark.parametrize('compress', [False, True])
def test_escaped_name_pdf(compress):
    document = pydyf.PDF()
    document.info['CustomName'] = pydyf.name('price%off{sale}')
    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
    }))
    pdf = io.BytesIO()
    document.write(pdf, compress=compress)
    result = run([
        'gs', '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER',
        '-dPDFSTOPONERROR', '-dPDFSTOPONWARNING', '-sDEVICE=nullpage', '-'],
        input=pdf.getvalue(), stdout=PIPE, stderr=PIPE)
    assert result.returncode == 0, result.stdout + result.stderr
