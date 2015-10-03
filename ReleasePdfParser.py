import sys
import os
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

def with_pdf (pdf_doc, fn, pdf_pwd, *args):
    """Open the pdf document, and apply the function, returning the results"""
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

def to_bytestring (s, enc='utf-8'):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)

def update_page_text_hash (h, lt_obj, pct=0.2):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""

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
		if not (to_bytestring(lt_obj.get_text())) == ' \n':# or not ((to_bytestring(lt_obj.get_text())) == '      \n'):
			new_str = to_bytestring(lt_obj.get_text()).strip(' \n\t\r')
			v.append(new_str)
			h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        h[(x0,x1)] = [to_bytestring(lt_obj.get_text())]

    return h

import csv

def parse_lt_objs (lt_objs, page_number, text=[]):
    text_content = [] 

    page_text = {} # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            # text, so arrange is logically based on its column width
            page_text = update_page_text_hash(page_text, lt_obj)

	#For Image/Picturs     
        #elif isinstance(lt_obj, LTImage):
    
    of = open("Final.txt","w")
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

def _parse_pages (doc):
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    #text_content = []
    for i, page in enumerate(PDFPage.create_pages(doc)):
	    interpreter.process_page(page)
       	    # receive the LTPage object for this page
       	    layout = device.get_result()
       	    # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
	    parse_lt_objs(layout, (i+1))

def get_pages (pdf_doc, pdf_pwd=''):
    return with_pdf(pdf_doc, _parse_pages, pdf_pwd)


if __name__=="__main__":
	if get_pages("xxxx")=="Error":
		print("Some Error in Opening File-Check File/File Location")
	else:
		print("Information Extracted")
