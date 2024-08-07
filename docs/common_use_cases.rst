Common Use Cases
================

pydyf has been created for WeasyPrint and many common use cases can thus be
found in `its repository`_.

.. _its repository: https://github.com/Kozea/WeasyPrint


Draw rectangles and lines
-------------------------

.. code-block:: python

   import pydyf

   document = pydyf.PDF()

   draw = pydyf.Stream()

   # Draw a first rectangle
   # With the border in dash style
   # The dash line is 2 points full, 1 point empty
   # And the dash line begins with 2 full points
   draw.rectangle(100, 100, 50, 70)
   draw.set_dash([2, 1], 0)
   draw.stroke()

   # Draw a second rectangle
   # The dash is reset to a full line
   # The line width is set
   # Move the bottom-left corner to (80, 80)
   # Fill the rectangle
   draw.rectangle(50, 50, 20, 40)
   draw.set_dash([], 0)
   draw.set_line_width(10)
   draw.set_matrix(1, 0, 0, 1, 80, 80)
   draw.fill()

   # Add the stream with the two rectangles into the document
   document.add_object(draw)

   # Add a page to the document containing the draw
   document.add_page(pydyf.Dictionary({
       'Type': '/Page',
       'Parent': document.pages.reference,
       'Contents': draw.reference,
       'MediaBox': pydyf.Array([0, 0, 200, 200]),
   }))

   # Write to document.pdf
   with open('document.pdf', 'wb') as f:
       document.write(f)

Add some color
--------------

.. code-block:: python

   import pydyf

   document = pydyf.PDF()

   draw = pydyf.Stream()

   # Set the color for nonstroking and stroking operations
   # Red for nonstroking an green for stroking
   draw.set_color_rgb(1.0, 0.0, 0.0)
   draw.set_color_rgb(0.0, 1.0, 0.0, stroke=True)
   draw.rectangle(100, 100, 50, 70)
   draw.set_dash([2, 1], 0)
   draw.stroke()
   draw.rectangle(50, 50, 20, 40)
   draw.set_dash([], 0)
   draw.set_line_width(10)
   draw.set_matrix(1, 0, 0, 1, 80, 80)
   draw.fill()

   document.add_object(draw)

   document.add_page(pydyf.Dictionary({
       'Type': '/Page',
       'Parent': document.pages.reference,
       'Contents': draw.reference,
       'MediaBox': pydyf.Array([0, 0, 200, 200]),
   }))

   with open('document.pdf', 'wb') as f:
       document.write(f)

Display image
-------------

.. code-block:: python

   import pydyf

   document = pydyf.PDF()

   extra = pydyf.Dictionary({
       'Type': '/XObject',
       'Subtype': '/Image',
       'Width': 197,
       'Height': 101,
       'ColorSpace': '/DeviceRGB',
       'BitsPerComponent': 8,
       'Filter': '/DCTDecode',
   })

   image = open('logo.jpg', 'rb').read()
   xobject = pydyf.Stream([image], extra=extra)
   document.add_object(xobject)

   image = pydyf.Stream()
   image.push_state()
   image.set_matrix(100, 0, 0, 100, 100, 100)
   image.draw_x_object('Im1')
   image.pop_state()
   document.add_object(image)

   # Put the image in the resources of the PDF
   document.add_page(pydyf.Dictionary({
       'Type': '/Page',
       'Parent': document.pages.reference,
       'MediaBox': pydyf.Array([0, 0, 200, 200]),
       'Resources': pydyf.Dictionary({
           'ProcSet': pydyf.Array(['/PDF', '/ImageB']),
           'XObject': pydyf.Dictionary({'Im1': xobject.reference}),
       }),
       'Contents': image.reference,
    }))

   with open('document.pdf', 'wb') as f:
       document.write(f)

Display text
------------

.. code-block:: python

  import pydyf

  document = pydyf.PDF()

  # Define the font
  font = pydyf.Dictionary({
      'Type': '/Font',
      'Subtype': '/Type1',
      'Name': '/F1',
      'BaseFont': '/Helvetica',
      'Encoding': '/MacRomanEncoding',
  })

  document.add_object(font)

  # Set the font use for the text
  # Move to where to display the text
  # And display it
  text = pydyf.Stream()
  text.begin_text()
  text.set_font_size('F1', 20)
  text.set_text_matrix(1, 0, 0, 1, 10, 90)
  text.show_text(pydyf.String('Bœuf grillé & café'.encode('macroman')))
  text.end_text()

  document.add_object(text)

  # Put the font in the resources of the PDF
  document.add_page(pydyf.Dictionary({
      'Type': '/Page',
      'Parent': document.pages.reference,
      'MediaBox': pydyf.Array([0, 0, 200, 200]),
      'Contents': text.reference,
      'Resources': pydyf.Dictionary({
          'ProcSet': pydyf.Array(['/PDF', '/Text']),
          'Font': pydyf.Dictionary({'F1': font.reference}),
      })
  }))

  with open('document.pdf', 'wb') as f:
      document.write(f)


Add metadata
------------

.. code-block:: python

    import datetime

    import pydyf

    document = pydyf.PDF()
    document.info['Author'] = pydyf.String('Jane Doe')
    document.info['Creator'] = pydyf.String('pydyf')
    document.info['Keywords'] = pydyf.String('some keywords')
    document.info['Producer'] = pydyf.String('The producer')
    document.info['Subject'] = pydyf.String('An example PDF')
    document.info['Title'] = pydyf.String('A PDF containing metadata')
    now = datetime.datetime.now()
    document.info['CreationDate'] = pydyf.String(now.strftime('D:%Y%m%d%H%M%S'))

    document.add_page(
        pydyf.Dictionary(
            {
                'Type': '/Page',
                'Parent': document.pages.reference,
                'MediaBox': pydyf.Array([0, 0, 200, 200]),
            }
        )
    )

    # 550 bytes PDF
    with open('metadata.pdf', 'wb') as f:
        document.write(f)


Display inline QR-code image
----------------------------

.. code-block:: python

    import pydyf
    import qrcode

    # Create a QR code image
    image = qrcode.make('Some data here')
    raw_data = image.tobytes()
    width = image.size[0]
    height = image.size[1]

    document = pydyf.PDF()
    stream = pydyf.Stream(compress=True)
    stream.push_state()
    x = 0
    y = 0
    stream.set_matrix(width, 0, 0, height, x, y)
    # Add the 1-bit grayscale image inline in the PDF
    stream.inline_image(width, height, 'Gray', 1, raw_data)
    stream.pop_state()
    document.add_object(stream)

    # Put the image in the resources of the PDF
    document.add_page(
        pydyf.Dictionary(
            {
                'Type': '/Page',
                'Parent': document.pages.reference,
                'MediaBox': pydyf.Array([0, 0, 400, 400]),
                'Resources': pydyf.Dictionary(
                    {
                        'ProcSet': pydyf.Array(
                            ['/PDF', '/ImageB', '/ImageC', '/ImageI']
                        ),
                    }
                ),
                'Contents': stream.reference,
            }
        )
    )

    # 909 bytes PDF
    with open('qrcode.pdf', 'wb') as f:
        document.write(f, compress=True)

