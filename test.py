import google.generativeai as genai
import base64


genai.configure(api_key="AIzaSyAUtPX7slfhXnfwKPXnQOmFoVhevfC3L4c")

model = genai.GenerativeModel("gemini-1.5-flash")

# Path to your local PDF file
pdf_path = "/Users/rahulthakur/Desktop/practice_work/practice1/sample_invoice.pdf" 

  # Replace with your model name if needed

# Function to read PDF in binary mode
def read_pdf_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

# Function to process PDF with Gemini LLM
def process_pdf_with_gemini(pdf_data):

    doc_data = base64.standard_b64encode(pdf_data).decode("utf-8")
    prompt = "Extract this document. Output should be only extracted document and nothing else."

    try:
        response = model.generate_content([{'mime_type':'application/pdf', 'data': doc_data}, prompt])
        return response.text
    except Exception as e:
        print(f"Error processing PDF with Gemini: {e}")
        return None

# Main execution
pdf_data = read_pdf_binary(pdf_path)
if pdf_data:
    print("Processing PDF with Google's Gemini LLM...")
    processed_text = process_pdf_with_gemini(pdf_data)

    if processed_text:
        print("\nExtracted Text:\n")
        print(processed_text)
    else:
        print("Failed to extract text with Gemini.")
else:
    print("PDF file not found or unreadable. Please check the file path.")
