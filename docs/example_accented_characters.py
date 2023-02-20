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
text.set_font_size('F1', 10)
text.text_matrix(1, 0, 0, 1, 10, 180)
text.show_text(pydyf.String('Tête-à-tête på «Færøyene»?'.encode('mac_roman')))
text.end_text()

# Another line of text, this time colored
text.begin_text()
text.set_font_size('F1', 10)
text.set_color_rgb(0, 0.7, 0.4)
text.text_matrix(1, 0, 0, 1, 10, 160)
text.show_text(pydyf.String('Argüição…  Łódź!'.encode('mac_roman', errors='replace')))  # Ł and ź are not available
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

with open('../tests/document.pdf', 'wb') as f:
    document.write(f)


