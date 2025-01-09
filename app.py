import os
import io
import zipfile
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from werkzeug.utils import secure_filename
from convert_to_pdf import convert_docx_to_pdf

# Flask-instans
app = Flask(__name__)
app.secret_key = "some_secret_key"  # Krävs för flash-meddelanden

UPLOAD_FOLDER = "uploads"
TEMPLATE_FOLDER = "cert_template"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATE_FOLDER'] = TEMPLATE_FOLDER

def clear_upload_folder(folder):
    """Tar bort alla filer i en angiven mapp."""
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Fel vid borttagning av fil {file_path}: {e}")
    # Kontrollera att mappen är tom
    if os.listdir(folder):
        print(f"Varning: Mappen {folder} är inte tom efter rensning!")


# Rensa mappen vid appstart
clear_upload_folder(UPLOAD_FOLDER)

def allowed_file(filename):
    """Returnerar True om filen är en .docx."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def replace_text_in_runs(docx_path, replacements, output_path):
    """
    Öppnar docx_path, ersätter text (t.ex. "NAMN" -> studentens namn),
    och sparar i output_path.
    """
    from docx import Document
    doc = Document(docx_path)
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for old_text, new_text in replacements.items():
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)
    doc.save(output_path)

@app.route('/', methods=['GET'])
def index():
    """
    Visar startsidan med formulär för att ladda upp en Word-mall,
    ange kurskod, datum och studentnamn.
    """
    clear_upload_folder(app.config['UPLOAD_FOLDER'])  # Rensa uploads-mappen
    flash("Mappen har rensats för en ny session.", "info")
    today_str = date.today().strftime("%Y-%m-%d")
    return render_template('index.html', today=today_str)




@app.route('/', methods=['POST'])
def process_form():
    """
    Hanterar formulärdata: genererar .docx-filer för varje student.
    """
    kurskod = request.form.get('kurskod', '').strip()
    datum = request.form.get('datum', '').strip()
    if not datum:
        datum = date.today().strftime("%Y-%m-%d")

    student_list = request.form.get('student_list', '').strip()
    lines = [line.strip() for line in student_list.split('\n') if line.strip()]
    if not lines:
        flash("Inga studentnamn angivna!", "error")
        return redirect(url_for('index'))

    if 'docx_file' not in request.files:
        flash("Ingen Word-mall vald!", "error")
        return redirect(url_for('index'))

    file = request.files['docx_file']
    if file.filename == '':
        flash("Du valde ingen fil (filnamn saknas).", "error")
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash("Endast .docx-filer tillåtna!", "error")
        return redirect(url_for('index'))

    # Spara mallen i cert_template/-mappen
    template_filename = secure_filename(file.filename)
    template_path = os.path.join(TEMPLATE_FOLDER, template_filename)
    file.save(template_path)

    # Generera .docx för varje student
    for student_name in lines:
        out_filename_docx = f"Certifikat_{kurskod}_{student_name}_{datum}.docx"
        out_path_docx = os.path.join(app.config['UPLOAD_FOLDER'], out_filename_docx)

        replacements = {"NAMN": student_name, "KURSKOD": kurskod, "DATUM": datum}
        replace_text_in_runs(template_path, replacements, out_path_docx)

    flash("DOCX-filer skapades framgångsrikt!", "success")
    all_files = sorted([f for f in os.listdir(UPLOAD_FOLDER)])
    return render_template('done.html',
                           docx_files=[f for f in all_files if f.endswith('.docx')],
                           pdf_files=[f for f in all_files if f.endswith('.pdf')],
                           pdf_available=False)


@app.route('/convert_pdf', methods=['POST'])
def convert_pdf():
    """
    Anropar funktionen för att konvertera alla .docx i uploads/-mappen till .pdf.
    """
    folder = app.config['UPLOAD_FOLDER']

    try:
        success, message = convert_docx_to_pdf(folder)
        if success:
            flash("Alla filer konverterades till PDF!", "success")
        else:
            flash(message, "error")
    except Exception as e:
        flash(f"Fel vid PDF-konvertering: {str(e)}", "error")

    # Hämta aktuella filer efter konvertering
    all_files = sorted([f for f in os.listdir(UPLOAD_FOLDER)])
    pdf_files = [f for f in all_files if f.endswith('.pdf')]
    docx_files = [f for f in all_files if f.endswith('.docx')]

    # Kontrollera om PDF-filer finns
    if not pdf_files:
        flash("Inga PDF-filer skapades. Kontrollera dina DOCX-filer och försök igen.", "warning")

    return render_template('done.html',
                           docx_files=docx_files,
                           pdf_files=pdf_files)




@app.route('/download_template')
def download_template():
    """
    Skickar exempelmallen till användaren.
    """
    template_file = os.path.join(app.config['TEMPLATE_FOLDER'], 'exempelmall.docx')
    if not os.path.exists(template_file):
        flash("Exempelmallen finns inte!", "error")
        return redirect(url_for('index'))

    return send_file(template_file, as_attachment=True, download_name='exempelmall.docx')






@app.route('/download_zip/<file_type>', methods=['POST'])
def download_zip(file_type):
    """
    Packar alla DOCX- eller PDF-filer i en ZIP-fil och skickar den till användaren.
    """
    files_to_zip = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(f'.{file_type}')]
    if not files_to_zip:
        flash(f"Inga {file_type.upper()}-filer att ladda ner!", "error")
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
