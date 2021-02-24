import pydyf

from . import assert_pixels


def test_fill():
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
    ''')


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


def test_transform():
    document = pydyf.PDF()

    draw = pydyf.Stream()
    draw.move_to(2, 2)
    draw.set_line_width(2)
    draw.line_to(2, 5)
    draw.transform(1, 0, 0, 1, 1, 1)
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
    draw.text_matrix(1, 0, 0, 1, -20, 5)
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
        __________
        __________
        __________
        __________
        __________
    ''')
