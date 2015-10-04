import sys
import os
import csv
from binascii import b2a_hex


###
### pdf-miner requirements
###

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar

outputCSVFile = "Final.txt"
inputPdfFile = "xxxx"

def openPdf (pdf_doc, fn, pwd, *args):
    result = None
    try:
        # open the pdf file
        fp = open(pdf_doc, 'rb')
        # create a parser object associated with the file object
        parser = PDFParser(fp)
        # create a PDFDocument object that stores the document structure
        doc = PDFDocument(parser)
        # connect the parser and document objects
        parser.set_document(doc)

        if doc.is_extractable:
            # apply the function and return the result
	    result = fn(doc)

        # close the pdf file
        fp.close()
    except IOError:
        # the file doesn't exist or similar problem
	#print("Error in File opening")
     	result = "Error"
     	#pass
    return result


###
### Extracting Text
###
import re

def convertString (s, enc='utf-8'):
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

def parsePdfText (h, lt_obj, pct=0.2):

    x0 = lt_obj.bbox[0]
    x1 = lt_obj.bbox[2]

    key_found = False
    for k, v in h.items():
        hash_x0 = k[0]
        if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
            hash_x1 = k[1]
            if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
                # the text inside this LT* object was positioned at the same
                # width as a prior series of text, so it belongs together
                key_found = True
		if not (convertString(lt_obj.get_text())) == ' \n':
			new_str = convertString(lt_obj.get_text()).strip(' \n\t\r')
			v.append(new_str)
			h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        h[(x0,x1)] = [convertString(lt_obj.get_text())]

    return h



def parsePdfObjects (lt_objs, page_number, text=[]):
    page_text = {} # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            # text, so arrange is logically based on its column width
            page_text = parsePdfText(page_text, lt_obj)

	#For Image/Picturs     
        #elif isinstance(lt_obj, LTImage):
    
    of = open(outputCSVFile,"w")
    ow = csv.writer(of,delimiter='#',lineterminator='\n\n')
    for k, v in sorted([(key,value) for (key,value) in page_text.items()]):
        # sort the page_text hash by the keys (x0,x1 values of the bbox),
        # which produces a top-down, left-to-right sequence of related columns

	lst=[]
	#Remove New Line Entry From CSV file Entry
	if v[0] != ' \n':
		for i in v:
			lst.append(i.strip(' \n'))
		ow.writerow(lst)
    of.close()


###
### Processing Pages
###

def parsePdf (doc):
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for i, page in enumerate(PDFPage.create_pages(doc)):
	    interpreter.process_page(page)
       	    # receive the LTPage object for this page
       	    layout = device.get_result()
       	    # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
	    parsePdfObjects(layout, (i+1))

def main (pdf_doc, pwd=''):
    return openPdf(pdf_doc, parsePdf, pwd)


if __name__=="__main__":
	if main(inputPdfFile)=="Error":
		print("Some Error in Opening File-Check File/File Location")
	else:
		print("Information Extracted")

