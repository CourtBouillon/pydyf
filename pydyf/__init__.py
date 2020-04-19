"""
pydyf − Low-level PDF generator

"""

from codecs import BOM_UTF16_BE
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
        return b'\n'.join((
            f'{self.number} {self.generation} obj'.encode('ascii'),
            self.data,
            b'endobj',
        ))

    @property
    def reference(self):
        return f'{self.number} {self.generation} R'

    @property
    def data(self):
        raise NotImplementedError()


class Dictionary(Object, dict):
    def __init__(self, values=None):
        Object.__init__(self)
        dict.__init__(self, values or {})

    @property
    def data(self):
        result = [b'<<']
        for key, value in self.items():
            if isinstance(value, Object):
                value = value.data
            elif not isinstance(value, bytes):
                value = str(value).encode('ascii')
            if isinstance(key, str):
                key = key.encode('ascii')
            result.append(b'/' + key + b' ' + value)
        result.append(b'>>')
        return b'\n'.join(result)


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

    def set_color_rgb(self, r, g, b, stroke=False):
        self.stream.append(f'{r} {g} {b} RG' if stroke else f'{r} {g} {b} rg')

    def set_dash(self, dash_array, dash_phase):
        self.stream.append(
            f'{Array(dash_array).data.decode("ascii")} {dash_phase} d')

    def set_line_width(self, width):
        self.stream.append(f'{width} w')

    def set_state(self, state_name):
        self.stream.append(f'/{state_name} gs')

    def stroke(self):
        self.stream.append('S')

    def stroke_and_close(self):
        self.stream.append('s')

    def transform(self, a, b, c, d, e, f):
        self.stream.append(f'{a} {b} {c} {d} {e} {f} cm')

    @property
    def data(self):
        result = []
        for item in self.stream:
            if isinstance(item, Object):
                item = item.data
            elif isinstance(item, str):
                item = item.encode('ascii')
            result.append(item)
        stream = b'\n'.join(result)
        return b'\n'.join((
            b'<< /Length ' + str(len(stream) + 1).encode('ascii') + b' >>',
            b'stream',
            stream,
            b'endstream',
        ))


class String(Object):
    def __init__(self, string):
        super().__init__()
        self.string = string

    @property
    def data(self):
        if isinstance(self.string, str):
            try:
                encoded_str = self.string.encode('ascii')
            except UnicodeEncodeError:
                encoded_str = BOM_UTF16_BE + self.string.encode('utf-16-be')
            return b'(' + encoded_str + b')'
        return b'(' + self.string + b')'


class Array(Object, list):
    def __init__(self, array=None):
        Object.__init__(self)
        list.__init__(self, array or [])

    @property
    def data(self):
        result = [b'[']
        for child in self:
            if isinstance(child, Object):
                child = child.data
            elif not isinstance(child, bytes):
                child = str(child).encode('ascii')
            result.append(child)
        result.append(b']')
        return b' '.join(result)


class PDF:
    def __init__(self):
        self.objects = []

        zero_object = Object()
        zero_object.generation = 65535
        zero_object.free = 'f'
        zero_object._indirect = ''
        self.add_object(zero_object)

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
            'Pages': self.pages.reference,
        })
        self.add_object(self.catalog)

        self.current_position = 0
        self.xref_position = None

    def add_page(self, page):
        self.pages['Count'] += 1
        self.add_object(page)
        self.pages['Kids'].extend([page.number, 0, 'R'])

    def add_object(self, object_):
        object_.number = len(self.objects)
        self.objects.append(object_)

    def write_line(self, content, output):
        self.current_position += len(content) + 1
        output.write(content + b'\n')

    def write_object(self, object_, output):
        for line in object_.data.split(b'\n'):
            self.write_line(line, output)

    def write_header(self, output):
        self.write_line(b'%PDF-1.7', output)

    def write_body(self, output):
        for object_ in self.objects:
            if object_.free == 'f':
                continue
            object_.offset = self.current_position
            self.write_line(object_.indirect, output)

    def write_cross_reference_table(self, output):
        self.write_line(b'xref', output)
        self.xref_position = self.current_position
        self.write_line(f'0 {len(self.objects)}'.encode('ascii'), output)
        for object_ in self.objects:
            self.write_line(
                (f'{object_.offset:010} {object_.generation:05} '
                 f'{object_.free} ').encode('ascii'), output
            )

    def write_trailer(self, output):
        self.write_line(b'trailer', output)
        self.write_object(Dictionary({
            'Size': len(self.objects),
            'Root': self.catalog.reference,
            'Info': self.info.reference,
        }), output)
        self.write_line(b'startxref', output)
        self.write_line(str(self.xref_position).encode('ascii'), output)
        self.write_line(b'%%EOF', output)

    def write(self, output=sys.stdout.buffer):
        self.write_header(output)
        self.write_body(output)
        self.write_cross_reference_table(output)
        self.write_trailer(output)
