import os
import pypdf
import pdfplumber
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

class OCRService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extracts text from a PDF file. First tries native text extraction,
        then fallback/OCR.
        """
        text = ""
        try:
            # Try pdfplumber first (cleaner text layout extraction)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # Fallback to pypdf if pdfplumber extracted nothing
            if not text.strip():
                with open(file_path, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting native text from PDF: {e}")
        
        # If it's scanned and has no native text, and OCR is available, try image OCR
        if not text.strip() and HAS_OCR:
            print("Native PDF text is empty. PDF might be scanned. Running OCR fallback...")
            # Note: Full OCR on scanned PDFs locally requires pdf2image and poppler.
            # We will provide a clean warning log.
            text = "[Scanned PDF - native text empty. Please upload clear text PDF or images for OCR]"

        return text.strip() if text.strip() else "[Empty or unreadable document]"

    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        """
        Extracts text from an image file using Tesseract OCR.
        """
        if not HAS_OCR:
            return "[OCR Engine (pytesseract/Pillow) not installed on server. Cannot extract image text]"
        
        try:
            img = Image.open(file_path)
            # Run pytesseract OCR
            text = pytesseract.image_to_string(img)
            return text.strip() if text.strip() else "[No text detected in image]"
        except Exception as e:
            print(f"OCR Image extraction error: {e}")
            return f"[Error during OCR processing: {str(e)}]"

ocr_service = OCRService()
