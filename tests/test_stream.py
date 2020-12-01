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

    graphic_state = pydyf.Dictionary({
        'Type': '/ExtGState',
        'SA': 'true',
    })
    document.add_object(graphic_state)

    draw = pydyf.Stream()
    draw.set_state('GS1')
    draw.rectangle(2, 2, 5, 6)
    draw.set_line_width(2)
    draw.stroke()
    document.add_object(draw)

    document.add_page(pydyf.Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'Contents': draw.reference,
        'MediaBox': pydyf.Array([0, 0, 10, 10]),
        'Resources': pydyf.Dictionary({
            'ExtGState': pydyf.Dictionary({'GS1': graphic_state.reference}),
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
