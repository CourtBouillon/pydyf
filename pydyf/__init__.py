"""
pydyf − Low-level PDF generator

"""

import sys

VERSION = __version__ = '0.0.1'


class Object:
    def __init__(self):
        self.number = None
        self.offset = 0
        self.generation = 0
        self.free = 'n'
        self._indirect = None

    @property
    def indirect(self):
        return '\n'.join((
            f'{self.number} {self.generation} obj',
            self.data,
            'endobj',
        ))

    @property
    def reference(self):
        return f'{self.number} {self.generation} R'

    @property
    def data(self):
        raise NotImplementedError()


class Dictionary(Object):
    def __init__(self, values):
        super().__init__()
        self.values = values

    @property
    def data(self):
        result = ['<<']
        for key, value in self.values.items():
            if isinstance(value, Object):
                value = value.data
            result.append(f'/{key} {value}')
        result.append('>>')
        return '\n'.join(result)


class Stream(Object):
    def __init__(self, stream=None):
        super().__init__()
        self.stream = stream or []

    def clip(self, even_odd=False):
        self.stream.append('W*' if even_odd else 'W')

    def close(self):
        self.stream.append('h')

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        self.stream.append(f'{x1} {y1} {x2} {y2} {x3} {y3} c')

    def end(self):
        self.stream.append('n')

    def fill(self, even_odd=False):
        self.stream.append('f*' if even_odd else 'f')

    def fill_and_stroke(self, even_odd=False):
        self.stream.append('B*' if even_odd else 'B')

    def fill_stroke_and_close(self, even_odd=False):
        self.stream.append('b*' if even_odd else 'b')

    def line_to(self, x, y):
        self.stream.append(f'{x} {y} l')

    def move_to(self, x, y):
        self.stream.append(f'{x} {y} m')

    def pop_state(self):
        self.stream.append('Q')

    def push_state(self):
        self.stream.append('q')

    def rectangle(self, x, y, width, height):
        self.stream.append(f'{x} {y} {width} {height} re')

    def set_dash(self, dash_array, dash_phase):
        self.stream.append(f'{dash_array.data} {dash_phase} d')

    def set_line_width(self, width):
        self.stream.append(f'{width} w')

    def set_color_rgb(self, r, g, b, stroke=False):
        self.stream.append(f'{r} {g} {b} RG' if stroke else f'{r} {g} {b} rg')

    def stroke(self):
        self.stream.append('s')

    def stroke_and_close(self):
        self.stream.append('S')

    def transform(self, a, b, c, d, e, f):
        self.stream.append(f'{a} {b} {c} {d} {e} {f} cm')

    @property
    def data(self):
        result = []
        for item in self.stream:
            if isinstance(item, Object):
                item = item.data
            result.append(item)
        stream = '\n'.join(result)
        return '\n'.join((
            f'<< /Length {len(stream) + 1} >>',
            'stream',
            stream,
            'endstream',
        ))


class String(Object):
    def __init__(self, string):
        super().__init__()
        self.string = string

    @property
    def data(self):
        return f'( {self.string} )'


class Array(Object):
    def __init__(self, array):
        super().__init__()
        self.array = array

    @property
    def data(self):
        result = ['[']
        for child in self.array:
            if isinstance(child, Object):
                child = child.data
            result.append(str(child))
        result.append(']')
        return ' '.join(result)


class PDF:
    def __init__(self):
        self.objects = []

        zero_object = Object()
        zero_object.generation = 65535
        zero_object.free = 'f'
        zero_object._indirect = ''
        self.add_object(zero_object)

        self.outlines = Dictionary({
            'Type': '/Outlines',
            'Count': 0,
        })
        self.add_object(self.outlines)

        self.pages = Dictionary({
            'Type': '/Pages',
            'Kids': Array([]),
            'Count': 0,
        })
        self.add_object(self.pages)

        self.info = Dictionary({})
        self.add_object(self.info)

        self.catalog = Dictionary({
            'Type': '/Catalog',
            'Outlines': self.outlines.reference,
            'Pages': self.pages.reference,
        })
        self.add_object(self.catalog)

        self.current_position = 0
        self.xref_position = None

    def add_page(self, page):
        self.pages.values['Count'] += 1
        self.add_object(page)
        self.pages.values['Kids'].array.extend([page.number, 0, 'R'])

    def add_object(self, object_):
        object_.number = len(self.objects)
        self.objects.append(object_)

    def write_line(self, content, output):
        self.current_position += len(content) + 1
        output.write((content + '\n').encode('ascii'))

    def write_object(self, object_, output):
        for line in object_.data.split('\n'):
            self.write_line(line, output)

    def write_header(self, output):
        self.write_line('%PDF-1.7', output)

    def write_body(self, output):
        for object_ in self.objects:
            if object_.free == 'f':
                continue
            object_.offset = self.current_position
            self.write_line(object_.indirect, output)

    def write_cross_reference_table(self, output):
        self.write_line('xref', output)
        self.xref_position = self.current_position
        self.write_line(f'0 {len(self.objects)}', output)
        for object_ in self.objects:
            self.write_line(
                f'{object_.offset:010} {object_.generation:05} '
                f'{object_.free} ', output
            )

    def write_trailer(self, output):
        self.write_line('trailer', output)
        self.write_object(Dictionary({
            'Size': len(self.objects),
            'Root': self.catalog.reference,
            'Info': self.info.reference,
        }), output)
        self.write_line('startxref', output)
        self.write_line(str(self.xref_position), output)
        self.write_line('%%EOF', output)

    def write(self, output=sys.stdout.buffer):
        self.write_header(output)
        self.write_body(output)
        self.write_cross_reference_table(output)
        self.write_trailer(output)


if __name__ == '__main__':
    document = PDF()

#    text = Stream((
#        'BT',
#        '/F1 24 Tf',
#        '10 90 Td',
#        String('Hello World'),
#        'Tj',
#        'ET',
#    ))
    draw = Stream()
    draw.set_color_rgb(1.0, 0.0, 0.0)
    draw.set_color_rgb(0.0, 1.0, 0.0, stroke=True)
    draw.rectangle(100, 100, 50, 70)
    draw.set_dash(Array([2, 1]), 0)
    draw.stroke()
    draw.rectangle(50, 50, 20, 40)
    draw.set_dash(Array([]), 0)
    draw.set_line_width(10)
    draw.transform(1, 0, 0, 1, 80, 80)
    draw.fill()
    draw.stroke()
    document.add_object(draw)

    font = Dictionary({
        'Type': '/Font',
        'Subtype': '/Type1',
        'Name': '/F1',
        'BaseFont': '/Helvetica',
        'Encoding': '/MacRomanEncoding',
    })
    document.add_object(font)

    document.add_page(Dictionary({
        'Type': '/Page',
        'Parent': document.pages.reference,
        'MediaBox': Array([0, 0, 200, 200]),
        'Contents': draw.reference,
        'Resources': Dictionary({
            'ProcSet': Array(['/PDF', '/Text']),
            'Font': Dictionary({'F1': font.reference}),
        })
    }))

    # stream = Stream()
    # stream.move_to(0, 0)
    # stream.line_to(3, 3)
    # stream.set_color(0, 0, 0, 0)
    # stream.stroke()
    # document.add_object(stream)

    # document.add_page(Dictionary({
    #     'Type': '/Page',
    #     'Parent': document.pages.reference,
    #     'MediaBox': Array([0, 0, 200, 200]),
    #     'Contents': stream.reference,
    #     'Resources': Dictionary({
    #         'ProcSet': Array(['/PDF', '/Text']),
    #         'Font': Dictionary({'F1': font.reference})
    #     }),
    # }))
    document.write()
