import os
import io
import zipfile
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from werkzeug.utils import secure_filename
from convert_to_pdf import convert_docx_to_pdf
from docx import Document
from lxml import etree
import subprocess



# Flask Application Instance
app = Flask(__name__)
app.secret_key = "some_secret_key"  # Required for flash messages

# Configuration
UPLOAD_FOLDER = "uploads"
TEMPLATE_FOLDER = "cert_template"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATE_FOLDER'] = TEMPLATE_FOLDER

# Ensure UPLOAD_FOLDER exists
upload_folder = app.config['UPLOAD_FOLDER']
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

def clear_upload_folder(folder):
    """
    Removes all files in the specified folder.
    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
    if os.listdir(folder):
        print(f"Warning: The folder {folder} is not empty after clearing!")

# Clear the upload folder at app startup
clear_upload_folder(UPLOAD_FOLDER)

def allowed_file(filename):
    """
    Checks if the uploaded file is a .docx file.

    Args:
        filename (str): The name of the uploaded file.

    Returns:
        bool: True if the file is allowed, otherwise False.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def replace_text_in_document(docx_path, replacements, output_path):
    """
    Replaces text in both the main content and text boxes (shapes) of a Word document.

    Args:
        docx_path (str): Path to the source .docx file.
        replacements (dict): Dictionary of text replacements {old_text: new_text}.
        output_path (str): Path to save the modified .docx file.
    """
    from docx import Document

    # Load the document
    doc = Document(docx_path)

    # Namespace mapping
    namespaces = {
        'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        'wps': "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
    }

    # Replace text in paragraphs
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for old_text, new_text in replacements.items():
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)

    # Replace text in shapes (text boxes)
    xpath_expression = etree.XPath('.//wps:txbx/w:txbxContent//w:t', namespaces=namespaces)
    for shape in xpath_expression(doc.element.body):
        if shape.text:
            for old_text, new_text in replacements.items():
                if old_text in shape.text:
                    shape.text = shape.text.replace(old_text, new_text)

    # Save the updated document
    doc.save(output_path)



@app.route('/', methods=['GET'])
def index():
    """
    Displays the index page with a form to upload a Word template,
    specify course code, date, and student names.
    """
    clear_upload_folder(app.config['UPLOAD_FOLDER'])  # Clear uploads folder
    flash("The upload folder has been cleared for a new session.", "info")
    today_str = date.today().strftime("%Y-%m-%d")
    return render_template('index.html', today=today_str)

@app.route('/', methods=['POST'])
def process_form():
    """
    Handles form data: generates .docx files for each student.
    """
    kurskod = request.form.get('kurskod', '').strip()
    datum = request.form.get('datum', '').strip() or date.today().strftime("%Y-%m-%d")

    student_list = request.form.get('student_list', '').strip()
    lines = [line.strip() for line in student_list.split('\n') if line.strip()]
    if not lines:
        flash("No student names provided!", "error")
        return redirect(url_for('index'))

    if 'docx_file' not in request.files:
        flash("No Word template selected!", "error")
        return redirect(url_for('index'))

    file = request.files['docx_file']
    if file.filename == '':
        flash("No file selected.", "error")
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash("Only .docx files are allowed!", "error")
        return redirect(url_for('index'))

    # Save the template in the cert_template/ folder
    template_filename = secure_filename(file.filename)
    template_path = os.path.join(TEMPLATE_FOLDER, template_filename)
    file.save(template_path)

    # Generate .docx files for each student
    for student_name in lines:
        out_filename_docx = f"Certifikat_{kurskod}_{student_name}_{datum}.docx"
        out_path_docx = os.path.join(app.config['UPLOAD_FOLDER'], out_filename_docx)

        replacements = {"NAMN": student_name, "KURSKOD": kurskod, "DATUM": datum}
        replace_text_in_document(template_path, replacements, out_path_docx)

    flash("DOCX files were successfully created!", "success")
    all_files = sorted([f for f in os.listdir(UPLOAD_FOLDER)])
    return render_template('done.html',
                           docx_files=[f for f in all_files if f.endswith('.docx')],
                           pdf_files=[f for f in all_files if f.endswith('.pdf')],
                           pdf_available=False)

@app.route('/convert_pdf', methods=['POST'])
def convert_pdf():
    folder = app.config['UPLOAD_FOLDER']
    docx_files = [f for f in os.listdir(folder) if f.endswith('.docx')]

    if not docx_files:
        flash("No DOCX files to convert!", "error")
        return redirect(url_for('index'))

    # Test LibreOffice
    try:
        check_result = subprocess.run(["python", "convert_to_pdf.py", "--check"], capture_output=True, text=True, check=True)
        app.logger.info(f"LibreOffice check passed: {check_result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        app.logger.error(f"LibreOffice check failed: {e.stderr.strip()}")
        flash(f"LibreOffice check failed: {e.stderr.strip()}", "error")
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Unexpected error during LibreOffice check: {e}")
        flash("Unexpected error during LibreOffice check.", "error")
        return redirect(url_for('index'))

    # Kör PDF-konvertering
    try:
        conversion_result = subprocess.run(["python", "convert_to_pdf.py", folder], capture_output=True, text=True, check=True)
        app.logger.info(f"PDF conversion output: {conversion_result.stdout.strip()}")
        flash("All files were successfully converted to PDF!", "success")
    except subprocess.CalledProcessError as e:
        app.logger.error(f"PDF conversion failed: {e.stderr.strip()}")
        flash(f"PDF conversion failed: {e.stderr.strip()}", "error")
    except Exception as e:
        app.logger.error(f"Unexpected error during PDF conversion: {e}")
        flash("An unexpected error occurred during PDF conversion.", "error")

    all_files = sorted([f for f in os.listdir(folder)])
    pdf_files = [f for f in all_files if f.endswith('.pdf')]
    docx_files = [f for f in all_files if f.endswith('.docx')]

    return render_template('done.html', docx_files=docx_files, pdf_files=pdf_files)




@app.route('/download_template')
def download_template():
    """
    Sends the example template to the user.
    """
    template_file = os.path.join(app.config['TEMPLATE_FOLDER'], 'exempelmall.docx')
    if not os.path.exists(template_file):
        flash("The example template does not exist!", "error")
        return redirect(url_for('index'))

    return send_file(template_file, as_attachment=True, download_name='exempelmall.docx')

@app.route('/download_zip/<file_type>', methods=['POST'])
def download_zip(file_type):
    """
    Packs all DOCX or PDF files into a ZIP file and sends it to the user.
    """
    files_to_zip = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(f'.{file_type}')]
    if not files_to_zip:
        flash(f"No {file_type.upper()} files to download!", "error")
        return redirect(url_for('index'))

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in files_to_zip:
            file_path = os.path.join(UPLOAD_FOLDER, fname)
            zf.write(file_path, arcname=fname)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'certifikat_{file_type}.zip'
    )

if __name__ == "__main__":
    app.run(debug=True)