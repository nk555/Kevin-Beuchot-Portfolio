import PyPDF2

class parser():
    def __init__(self, files):
        self.pdfs=[]
        for file in files:
            pdfFile = open(file, 'rb')
            self.pdfs.append(PyPDF2.PdfFileReader(pdfFile))
