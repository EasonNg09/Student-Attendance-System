import re
from PyPDF2 import PdfReader

def extract_specific_words(pdf_path, index_number_pattern):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            index_number_matches = []
            for page_num in range(len(pdf_reader.pages)):
                page_text = pdf_reader.pages[page_num].extract_text()

                matches = re.findall(index_number_pattern, page_text)
                index_number_matches.extend(matches)

            return index_number_matches
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

# if __name__ == "__main__":
#     pdf_path = r"C:/FYPCode/Uploads\authorisationslip_22WMR05689.pdf"

#     # Define the index number pattern
#     index_number_pattern = re.compile(r'\bW\w{9}\b')

#     # Call the extract_specific_words function with the index number pattern
#     extracted_index_numbers = extract_specific_words(pdf_path, index_number_pattern)

#     # Print the extracted index numbers
#     if extracted_index_numbers:
#         for index_number in extracted_index_numbers:
#             print(index_number)
#     else:
#         print("No index numbers extracted.")