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

    def clip(self):
        self.stream.append('W')

    def close(self):
        self.stream.append('h')

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        self.stream.append(f'{x1} {y1} {x2} {y2} {x3} {y3} c')

    def end(self):
        self.stream.append('n')

    def fill(self, rule='winding'):
        if rule == 'winding':
            self.stream.append('f')
        elif rule == 'even-odd':
            self.stream.append('f*')

    def fill_and_stroke(self, rule='winding'):
        if rule == 'winding':
            self.stream.append('B')
        elif rule == 'even-odd':
            self.stream.append('B*')

    def fill_stroke_and_close(self, rule='winding'):
        if rule == 'winding':
            self.stream.append('b')
        elif rule == 'even-odd':
            self.stream.append('b*')

    def line_to(self, x, y):
        self.stream.append(f'{x} {y} l')

    def move_to(self, x, y):
        if self.stream and self.stream[-1][-1] == 'm':
            self.stream.pop(-1)
        self.stream.append(f'{x} {y} m')

    def rectangle(self, x, y, width, height):
        self.stream.append(f'{x} {y} {width} {height} re')

    def stroke(self):
        self.stream.append('s')

    def stroke_and_close(self):
        self.stream.append('S')

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

    def write_line(self, content):
        self.current_position += len(content) + 1
        print(content, end='\n')

    def write_object(self, object_):
        for line in object_.data.split('\n'):
            self.write_line(line)

    def write_header(self):
        self.write_line('%PDF-1.7')

    def write_body(self):
        for object_ in self.objects:
            if object_.free == 'f':
                continue
            object_.offset = self.current_position
            self.write_line(object_.indirect)

    def write_cross_reference_table(self):
        self.write_line('xref')
        self.xref_position = self.current_position
        self.write_line(f'0 {len(self.objects)}')
        for object_ in self.objects:
            self.write_line(
                f'{object_.offset:010} {object_.generation:05} {object_.free} '
            )

    def write_trailer(self):
        self.write_line('trailer')
        self.write_object(Dictionary({
            'Size': len(self.objects),
            'Root': self.catalog.reference,
            'Info': self.info.reference,
        }))
        self.write_line('startxref')
        self.write_line(str(self.xref_position))
        self.write_line('%%EOF')

    def write(self):
        self.write_header()
        self.write_body()
        self.write_cross_reference_table()
        self.write_trailer()


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
    draw.move_to(100, 150)
    draw.curve_to(127, 150, 150, 127, 150, 100)
    draw.curve_to(150, 73, 127, 50, 100, 50)
    draw.curve_to(73, 50, 50, 73, 50, 100)
    draw.curve_to(50, 127, 73, 150, 100, 150)
    draw.clip()
    draw.stroke()
    draw.move_to(25, 0)
    draw.line_to(25, 200)
    draw.stroke()
    draw.move_to(50, 0)
    draw.line_to(50, 200)
    draw.stroke()
    draw.move_to(75, 0)
    draw.line_to(75, 200)
    draw.stroke()
    draw.move_to(100, 0)
    draw.line_to(100, 200)
    draw.stroke()
    draw.move_to(125, 0)
    draw.line_to(125, 200)
    draw.stroke()
    draw.move_to(150, 0)
    draw.line_to(150, 200)
    draw.stroke()
    draw.move_to(175, 0)
    draw.line_to(175, 200)
    draw.stroke()
    draw.move_to(0, 25)
    draw.line_to(200, 25)
    draw.stroke()
    draw.move_to(0, 50)
    draw.line_to(200, 50)
    draw.stroke()
    draw.move_to(0, 75)
    draw.line_to(200, 75)
    draw.stroke()
    draw.move_to(0, 100)
    draw.line_to(200, 100)
    draw.stroke()
    draw.move_to(0, 125)
    draw.line_to(200, 125)
    draw.stroke()
    draw.move_to(0, 150)
    draw.line_to(200, 150)
    draw.stroke()
    draw.move_to(0, 175)
    draw.line_to(200, 175)
    draw.stroke()
    document.add_object(draw)

    draw2 = Stream()
    draw2.rectangle(100, 100, 50, 70)
    draw2.fill()
    draw2.stroke()
    document.add_object(draw2)

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
        'Contents': draw2.reference,
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
