
import os
import pdfplumber
import google.generativeai as genai
from fpdf import FPDF  # pip install fpdf

# Set your API key
os.environ["GOOGLE_API_KEY"] = "your api key"
# Use the correct environment variable name 'GOOGLE_API_KEY' to access the API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-pro")

def allowed_file(filename):
    allowed_extensions = {'pdf', 'txt', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def extract_text_from_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages])
        return text
    elif ext == 'docx':
        doc = docx.Document(file_path)
        text = ' '.join([para.text for para in doc.paragraphs])
        return text
    elif ext == 'txt':
        with open(file_path, 'r') as file:
            return file.read()
    return None

def Question_mcqs_generator(input_text, num_questions, difficulty):
    prompt = f"""
    You are an AI assistant helping the user generate multiple-choice questions (MCQs) based on the following text:
    '{input_text}'
    Please generate {num_questions} MCQs at a {difficulty} difficulty level. Each question should have:
    - A clear question
    - Four answer options (labeled A, B, C, D)
    - The correct answer clearly indicated
    Format:
    ## MCQ
    Question: [question]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    Correct Answer: [correct option]
    """
    response = model.generate_content(prompt).text.strip()
    return response

def save_mcqs_to_file(mcqs, filename):
    with open(filename, 'w') as f:
        f.write(mcqs)

def create_pdf(mcqs, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for mcq in mcqs.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)  # Add a line break

    pdf.output(filename)

def main():
    input_file = input("Enter the path of the file (pdf, txt, docx): ")

    if not allowed_file(input_file):
        print("Invalid file format. Please upload a pdf, txt, or docx file.")
        return

    num_questions = int(input("Enter the number of questions to generate: "))
    difficulty = input("Select difficulty level (easy, medium, hard): ").lower()

    if difficulty not in ["easy", "medium", "hard"]:
        print("Invalid difficulty level. Please choose from easy, medium, or hard.")
        return

    text = extract_text_from_file(input_file)
    if not text:
        print("Could not extract text from the file.")
        return

    mcqs = Question_mcqs_generator(text, num_questions, difficulty)

    txt_filename = "generated_mcqs.txt"
    pdf_filename = "generated_mcqs.pdf"

    save_mcqs_to_file(mcqs, txt_filename)
    create_pdf(mcqs, pdf_filename)

    print(f"MCQs have been saved to {txt_filename} and {pdf_filename}.")

if __name__ == "__main__":
    main()
