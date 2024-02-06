# importing all the required modules
import PyPDF2
#pip install pdfplumber
import pdfplumber
#pip install PyMuPDF

reader = PyPDF2.PdfReader("M111-10004_(PT22083).pdf")
#print('pages = ' + str(len(reader.pages)))
#print('lines = ' + str(len(reader.pages[0].extract_text().split('\n'))))
text_file = open("Output.txt", "w", encoding="utf-8")
for i in range(len(reader.pages)):
    text_file.write(reader.pages[i].extract_text())
text_file.close()
print("PyPDF2\n")
print(reader.pages[13].extract_text())
#print(reader.pages[1].extract_text())


with pdfplumber.open("M111-10004_(PT22083).pdf") as temp:
    first_page = temp.pages[0]    
    print("pdfplumber\n")
    print(temp.pages[13].extract_text())
    #print(temp.pages[1].extract_text())
    
import fitz # imports the pymupdf library
doc = fitz.open("M111-10004_(PT22083).pdf") # open a document
for page in doc: # iterate the document pages
  text = page.get_text() # get plain text encoded as UTF-8
print("pymupdf\n")
print(doc[13].get_text())
#print(doc[1].get_text())