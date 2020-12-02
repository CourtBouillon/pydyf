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
   draw.transform(1, 0, 0, 1, 80, 80)
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
   draw.transform(1, 0, 0, 1, 80, 80)
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

   extra = Dictionary({
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
   image.transform(100, 0, 0, 100, 100, 100)
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
  text.set_font_size('F1', 24)
  text.text_matrix(1, 0, 0, 1, 10, 90)
  text.show_text(pydyf.String('Hello World'))
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

