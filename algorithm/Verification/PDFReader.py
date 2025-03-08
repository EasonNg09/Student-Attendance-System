# from PyPDF2 import PdfReader

# def extract_bottom_text_from_pdf(pdf_path):
#     def extract_bottom(text, cm, tm, font_dict, font_size):
#         bottom_percentage = 50
#         y = tm[5]
#         page_height_points = 842 
#         bottom_height_points = (bottom_percentage / 100) * page_height_points
#         if bottom_height_points <= y:
#             parts.append(text)
#     reader = PdfReader(pdf_path)
#     page = reader.pages[0]
#     parts = []
#     page.extract_text(visitor_text=extract_bottom)
#     text_bottom = "".join(parts)
#     print(text_bottom)
#     return text_bottom

# if __name__ == "__main__":
#     #pdf_path = "C:\FYP Code/algorithm\(1)authorisationslip_22WMR05689.pdf"
#     pdf_path = r"C:/FYPCode/Uploads\authorisationslip_22WMR05689.pdf"
#     extracted_pdf_text = extract_bottom_text_from_pdf(pdf_path)
#     #print(extracted_pdf_text)

# will have problem when there are multiple pdf file in Upload folder
from PyPDF2 import PdfReader
import os

def extract_bottom_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        parts = []
        def extract_bottom(text, cm, tm, font_dict, font_size):
            bottom_percentage = 50
            y = tm[5]
            page_height_points = 842 
            bottom_height_points = (bottom_percentage / 100) * page_height_points
            if bottom_height_points <= y:
                parts.append(text)
        page.extract_text(visitor_text=extract_bottom)
        text_bottom = "".join(parts)
        print(f"Text extracted from {pdf_path}:\n{text_bottom}\n")
        return text_bottom
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    uploads_folder = os.path.join(os.getcwd(), 'Uploads')
    files_in_uploads = [f for f in os.listdir(uploads_folder) if os.path.isfile(os.path.join(uploads_folder, f))]
    pdf_files = [f for f in files_in_uploads if f.lower().endswith(".pdf")]
    for pdf_file_name in pdf_files:
        pdf_path = os.path.join(uploads_folder, pdf_file_name)
        extracted_pdf_text = extract_bottom_text_from_pdf(pdf_path)