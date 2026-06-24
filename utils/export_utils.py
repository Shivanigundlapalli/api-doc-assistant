import os
from fpdf import FPDF
import datetime

def export_chat_to_markdown(chat_history: list, output_dir: str = "data/exports") -> str:
    """
    Exports the chat history to a Markdown file.
    Returns the path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"chat_export_{timestamp}.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# API Documentation Assistant - Chat Export\n\n")
        f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        for msg in chat_history:
            f.write(f"### User\n{msg['question']}\n\n")
            f.write(f"### Assistant\n{msg['answer']}\n\n")
            f.write("---\n\n")
            
    return file_path

class ChatPDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 15)
        self.cell(0, 10, 'API Documentation Assistant Chat', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def export_chat_to_pdf(chat_history: list, output_dir: str = "data/exports") -> str:
    """
    Exports the chat history to a PDF file.
    Returns the path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"chat_export_{timestamp}.pdf")
    
    pdf = ChatPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("Arial", size=11)
    
    for msg in chat_history:
        # User Question
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(37, 99, 235) # Blue
        pdf.multi_cell(0, 10, f"User: {msg['question']}")
        
        # Assistant Answer
        pdf.set_font("Arial", '', 11)
        pdf.set_text_color(17, 24, 39) # Dark gray
        
        # Try to render the answer
        # We replace some unicode characters as fpdf standard fonts only support Latin1
        safe_answer = str(msg['answer']).encode('latin-1', 'ignore').decode('latin-1')
        
        # Split by lines and process manually to avoid FPDF width calculation bugs
        for line in safe_answer.split('\n'):
            if line.strip():
                # Manually split long lines into chunks to prevent "Not enough horizontal space" FPDF bug
                words = line.split()
                chunk = ""
                for word in words:
                    # Very basic word wrap approximation for FPDF
                    if len(chunk) + len(word) > 80:
                        try:
                            pdf.multi_cell(0, 8, txt=chunk)
                        except Exception:
                            pass
                        chunk = word + " "
                    else:
                        chunk += word + " "
                
                if chunk.strip():
                    try:
                        pdf.multi_cell(0, 8, txt=chunk.strip())
                    except Exception:
                        pass
            else:
                pdf.ln(4)
        
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.get_x(), pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
    pdf.output(file_path)
    return file_path
