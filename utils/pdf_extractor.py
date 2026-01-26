import pypdf

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file, chunked by page.
    
    Args:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        list of str: A list where each element is the text content of a page.
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return pages_text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return []

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        text = extract_text_from_pdf(sys.argv[1])
        print(f"Extracted {len(text)} pages.")
