"""
pydyf − Low-level PDF generator

"""

from codecs import BOM_UTF16_BE
import sys
import zlib

VERSION = __version__ = '0.0.1'


def _to_bytes(item):
    """Convert item to bytes."""
    if isinstance(item, bytes):
        return item
    elif isinstance(item, Object):
        return item.data
    elif isinstance(item, float):
        if item.as_integer_ratio()[1] == 1:
            return f'{int(item):d}'.encode('ascii')
        else:
            return f'{item:f}'.encode('ascii')
    elif isinstance(item, int):
        return f'{item:d}'.encode('ascii')
    return str(item).encode('ascii')


class Object:
    """Base class for PDF objects. Every object inherit from it.

    .. attribute:: number

        Number of the object.

    .. attribute:: offset

        Position in the PDF of the object.

    .. attribute:: generation

        Version number of the object, non-negative.

    .. attribute:: free

        Indicate if an object is used `n` or has been deleted `f` and
        therefore is free.

    .. automethod:: indirect

    .. automethod:: reference

    .. automethod:: data

    """
    def __init__(self):
        self.number = None
        self.offset = 0
        self.generation = 0
        self.free = 'n'
        self._indirect = None

    @property
    def indirect(self):
        """Indirect representation of an object."""
        return b'\n'.join((
            str(self.number).encode('ascii') + b' ' +
            str(self.generation).encode('ascii') + b' obj',
            self.data,
            b'endobj',
        ))

    @property
    def reference(self):
        """Object identifier."""
        return (
            str(self.number).encode('ascii') + b' ' +
            str(self.generation).encode('ascii') + b' R')

    @property
    def data(self):
        """Data contained in the object. Shall be defined in each subclass."""
        raise NotImplementedError()


class Dictionary(Object, dict):
    """PDF Dictionary object. Inherit from Python dict.

    .. attribute:: values
        Python dict

    """
    def __init__(self, values=None):
        Object.__init__(self)
        dict.__init__(self, values or {})

    @property
    def data(self):
        result = [b'<<']
        for key, value in self.items():
            result.append(b'/' + _to_bytes(key) + b' ' + _to_bytes(value))
        result.append(b'>>')
        return b'\n'.join(result)


class Stream(Object):
    """PDF Stream object.

    .. attribute:: stream
        Python array

    .. attribute:: extra
        Metadata containing at least the lenght of the Stream.

    .. attribute:: compress
        Compress the stream data if set to True. Default False.

    .. automethod:: begin_text
    .. automethod:: clip
    .. automethod:: close
    .. automethod:: color_space
    .. automethod:: curve_to
    .. automethod:: draw_x_object
    .. automethod:: end
    .. automethod:: end_text
    .. automethod:: fill
    .. automethod:: fill_and_stroke
    .. automethod:: fill_stroke_and_close
    .. automethod:: line_to
    .. automethod:: move_to
    .. automethod:: shading
    .. automethod:: pop_state
    .. automethod:: push_state
    .. automethod:: rectangle
    .. automethod:: set_color_rgb
    .. automethod:: set_color_special
    .. automethod:: set_dash
    .. automethod:: set_font_size
    .. automethod:: set_line_width
    .. automethod:: set_state
    .. automethod:: show_text
    .. automethod:: stroke
    .. automethod:: stroke_and_close
    .. automethod:: text_matrix
    .. automethod:: transform

    """
    def __init__(self, stream=None, extra=None, compress=False):
        super().__init__()
        self.stream = stream or []
        self.extra = extra or {}
        self.compress = compress

    def begin_text(self):
        """Begin a text object."""
        self.stream.append(b'BT')

    def clip(self, even_odd=False):
        """Modify the current clipping path by intersecting it with the
        current path.

        Use the nonzero winding number rule to determine which regions lie
        inside the clipping path by default.
        Use the even-odd rule if even_odd set to True.
        """
        self.stream.append(b'W*' if even_odd else b'W')

    def close(self):
        """Close the current subpath by appending a straight line segment from
        the current point to the starting point of the subpath.
        """
        self.stream.append(b'h')

    def color_space(self, space, stroke=False):
        """Set the nonstroking color space. If stroke is set to True, set the
        stroking color space."""
        self.stream.append(
            b'/' + _to_bytes(space) + b' ' + (b'CS' if stroke else b'cs'))

    def curve_to(self, x1, y1, x2, y2, x3, y3):
        """Add a cubic Bézier curve to the current path.

        The curve shall extend from (x3, y3) using (x1, y1) and (x2, y2) as the
        Bézier control points."""
        self.stream.append(b' '.join((
            _to_bytes(x1), _to_bytes(y1),
            _to_bytes(x2), _to_bytes(y2),
            _to_bytes(x3), _to_bytes(y3), b'c')))

    def draw_x_object(self, reference):
        """Draw the object given by reference."""
        self.stream.append(b'/' + _to_bytes(reference) + b' Do')

    def end(self):
        """End path without filling or stroking."""
        self.stream.append(b'n')

    def end_text(self):
        """End text object."""
        self.stream.append(b'ET')

    def fill(self, even_odd=False):
        """Fill path using nonzero winding rule. Use even-odd rule if even_odd
        is set to True."""
        self.stream.append(b'f*' if even_odd else b'f')

    def fill_and_stroke(self, even_odd=False):
        """Fill and stroke path usign nonzero winding rule. Use even-odd rule
        if even_odd is set to True."""
        self.stream.append(b'B*' if even_odd else b'B')

    def fill_stroke_and_close(self, even_odd=False):
        """Fill, stroke and close path using nonzero winding rule. Use
        even-odd rule if even_odd is set to True."""
        self.stream.append(b'b*' if even_odd else b'b')

    def line_to(self, x, y):
        """Add a line from the current point to the point (x, y)."""
        self.stream.append(b' '.join((_to_bytes(x), _to_bytes(y), b'l')))

    def move_to(self, x, y):
        """Begin a new subpath by moving the current point to (x, y)."""
        self.stream.append(b' '.join((_to_bytes(x), _to_bytes(y), b'm')))

    def shading(self, name):
        """Paint the shape and color shading described by the shading
        dictionary `name`."""
        self.stream.append(b'/' + _to_bytes(name) + b' sh')

    def pop_state(self):
        """Restore graphic state."""
        self.stream.append(b'Q')

    def push_state(self):
        """Save graphic state."""
        self.stream.append(b'q')

    def rectangle(self, x, y, width, height):
        """Add a rectangle to the current path as a complete subpath.

        (x, y) is the lower-left corner and width and height the dimensions.
        """
        self.stream.append(b' '.join((
            _to_bytes(x), _to_bytes(y),
            _to_bytes(width), _to_bytes(height), b're')))

    def set_color_rgb(self, r, g, b, stroke=False):
        """Set RGB color for nonstroking operations, for stroking operations if
        stroke is set to True."""
        self.stream.append(b' '.join((
            _to_bytes(r), _to_bytes(g), _to_bytes(b),
            (b'RG' if stroke else b'rg'))))

    def set_color_special(self, name, stroke=False):
        """Set color for nonstroking operations, for stroking operation if
        stroke is set to True."""
        self.stream.append(
            b'/' + _to_bytes(name) + b' ' + (b'SCN' if stroke else b'scn'))

    def set_dash(self, dash_array, dash_phase):
        """Set the dash line pattern.

        :param dash_array: Array defining the dash pattern
        :param dash_phase: Integer defining the start of the dash phase
        """
        self.stream.append(b' '.join((
            Array(dash_array).data, _to_bytes(dash_phase), b'd')))

    def set_font_size(self, font, size):
        """Set the font and its size."""
        self.stream.append(
            b'/' + _to_bytes(font) + b' ' + _to_bytes(size) + b' Tf')

    def set_line_width(self, width):
        """Set the line width."""
        self.stream.append(_to_bytes(width) + b' w')

    def set_state(self, state_name):
        """Set the specified parameters in the graphic state.

        :param state_name: graphic state parameter dictionary
        """
        self.stream.append(b'/' + _to_bytes(state_name) + b' gs')

    def show_text(self, text):
        """Show a text."""
        self.stream.append(b'[' + _to_bytes(text) + b'] TJ')

    def stroke(self):
        """Stroke path."""
        self.stream.append(b'S')

    def stroke_and_close(self):
        """Stroke and close path."""
        self.stream.append(b's')

    def text_matrix(self, a, b, c, d, e, f):
        """Set text matrix and text line matrix.

        :param a: top left number in the matrix
        :param b: top middle number in the matrix
        :param c: middle left number in the matrix
        :param d: middle middle number in the matrix
        :param e: bottom left number in the matrix
        :param f: bottom middle number in the matrix
        """
        self.stream.append(b' '.join((
            _to_bytes(a), _to_bytes(b), _to_bytes(c),
            _to_bytes(d), _to_bytes(e), _to_bytes(f), b'Tm')))

    def transform(self, a, b, c, d, e, f):
        """Modify the current transformation matrix by concatenating the
        specify matrix.

        :param a: top left number in the matrix
        :param b: top middle number in the matrix
        :param c: middle left number in the matrix
        :param d: middle middle number in the matrix
        :param e: bottom left number in the matrix
        :param f: bottom middle number in the matrix
        """
        self.stream.append(b' '.join((
            _to_bytes(a), _to_bytes(b), _to_bytes(c),
            _to_bytes(d), _to_bytes(e), _to_bytes(f), b'cm')))

    @property
    def data(self):
        stream = b'\n'.join(_to_bytes(item) for item in self.stream)
        extra = Dictionary(self.extra.copy())
        if self.compress:
            extra['Filter'] = '/FlateDecode'
            compressobj = zlib.compressobj()
            stream = compressobj.compress(stream)
            stream += compressobj.flush()
        extra['Length'] = len(stream) + 1
        return b'\n'.join((extra.data, b'stream', stream, b'endstream'))


class String(Object):
    """PDF String object.

    .. attribute:: string
        Classic string.
    """
    def __init__(self, string=''):
        super().__init__()
        self.string = string

    @property
    def data(self):
        try:
            return b'(' + _to_bytes(self.string) + b')'
        except UnicodeEncodeError:
            encoded = BOM_UTF16_BE + str(self.string).encode('utf-16-be')
            return b'<' + encoded.hex().encode('ascii') + b'>'


class Array(Object, list):
    """PDF Array object. Inherit from list.

    .. attribute:: array
        Python array.
    """
    def __init__(self, array=None):
        Object.__init__(self)
        list.__init__(self, array or [])

    @property
    def data(self):
        result = [b'[']
        for child in self:
            result.append(_to_bytes(child))
        result.append(b']')
        return b' '.join(result)


class PDF:
    """The PDF class.

    .. attribute:: objects

        Python array containing the objects of the PDF.

    .. attribute:: zero_object

        A PDF object which is the head of the list of free objects.

    .. attribute:: pages

        PDF dictionary containing the pages of the PDF.

    .. attribute:: info

        PDF dictionary containing the metadatas of the PDF.

    .. attribute:: catalog

        PDF dictionary containing references to the other objects.

    .. attribute:: current_position

        Current position in the PDF.

    .. attribute:: xref_position

        Position of the cross reference table.

    .. automethod:: add_page
    .. automethod:: add_object
    .. automethod:: write_line
    .. automethod:: write_object
    .. automethod:: write_header
    .. automethod:: write_body
    .. automethod:: write_cross_reference_table
    .. automethod:: write_trailer
    .. automethod:: write
    """
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
        """Add a page to the PDF.

        :param page: PDF dictionary of the page.
        """
        self.pages['Count'] += 1
        self.add_object(page)
        self.pages['Kids'].extend([page.number, 0, 'R'])

    def add_object(self, object_):
        """Add an object into the PDF."""
        object_.number = len(self.objects)
        self.objects.append(object_)

    def write_line(self, content, output):
        """Write a line into the output.

        :param content: content to write
        :param output: output
        """
        self.current_position += len(content) + 1
        output.write(content + b'\n')

    def write_object(self, object_, output):
        """Write an object into the output."""
        for line in object_.data.split(b'\n'):
            self.write_line(line, output)

    def write_header(self, output):
        """Write the PDF header into the output."""
        self.write_line(b'%PDF-1.7', output)

    def write_body(self, output):
        """Write all the objects of the PDF into the output.
        Except free objects.
        """
        for object_ in self.objects:
            if object_.free == 'f':
                continue
            object_.offset = self.current_position
            self.write_line(object_.indirect, output)

    def write_cross_reference_table(self, output):
        """Write the cross reference table into the output."""
        self.xref_position = self.current_position
        self.write_line(b'xref', output)
        self.write_line(f'0 {len(self.objects)}'.encode('ascii'), output)
        for object_ in self.objects:
            self.write_line(
                (f'{object_.offset:010} {object_.generation:05} '
                 f'{object_.free} ').encode('ascii'), output
            )

    def write_trailer(self, output):
        """Write the trailer into the output."""
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
        """Write the PDF into the output.

        :param output: the output, by default stdout.
        """
        self.write_header(output)
        self.write_body(output)
        self.write_cross_reference_table(output)
        self.write_trailer(output)
