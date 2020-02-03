import comtypes.client
from PyPDF4 import PdfFileReader, PdfFileWriter
import os


def PPTtoPDF(inputFileName, outputFileName, formatType = 32):
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = 1

    if outputFileName[-3:] != 'pdf':
        outputFileName = outputFileName + ".pdf"

    inputFileName = os.path.abspath(inputFileName)
    outputFileName = os.path.abspath(outputFileName)

    deck = powerpoint.Presentations.Open(inputFileName)
    deck.SaveAs(outputFileName, formatType) # formatType = 32 for ppt to pdf
    deck.Close()
    powerpoint.Quit()


if __name__ == '__main__':
    input_path = 'input.pptx'
    output_path = 'output.pdf'

    PPTtoPDF(input_path, output_path)

    pdf = PdfFileReader(output_path)

    for page_number in range(pdf.getNumPages()):
        pdf = PdfFileReader(output_path)
        page = pdf.getPage(page_number)

        writer = PdfFileWriter()
        writer.addPage(page)
        page_text = page.extractText().split('\n')

        for ingredients_index, text in enumerate(page_text):
            if ':' in text:
                break

        else:
            print(page_text)
            continue

        title = page_text[:ingredients_index]

        recipe_name = '_'.join(''.join(title).split()).lower().replace('\'', '').replace('&', 'and')
        print(recipe_name)

        path = os.path.join('recipe_website', 'pages', f'{recipe_name}.pdf')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as out:
            writer.write(out)
