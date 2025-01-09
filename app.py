import os
import io
import zipfile
import subprocess
import sys
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

#
# Försök installera/importera python-docx
#
try:
    import docx
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'python-docx'])
    import docx

#
# Flask-instans
#
app = Flask(__name__)
app.secret_key = "some-secret-key"  # Krävs för att flash() ska fungera

#
# Konfiguration
#
UPLOAD_FOLDER = 'uploads'          # Mapp för uppladdade + genererade filer
ALLOWED_EXTENSIONS = {'docx'}      # Endast docx
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Kollar om filen har filändelse .docx."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def replace_text_in_runs(docx_path, replacements, output_path):
    """
    Öppnar docx_path, ersätter text (ex "NAMN" -> "Studenten"),
    och sparar i output_path.
    """
    doc = docx.Document(docx_path)

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for old_text, new_text in replacements.items():
                if old_text in run.text:
                    run.text = run.text.replace(old_text, new_text)

    doc.save(output_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Start-/formulärsida:
      - Ladda upp .docx-fil
      - Ange kurskod, datum (default dagens datum)
      - Klistra in studentnamn
    """
    if request.method == 'POST':
        # Hämta formulärdata
        kurskod = request.form.get('kurskod', '').strip()
        datum = request.form.get('datum', '').strip()
        if not datum:
            datum = date.today().strftime("%Y-%m-%d")
        student_list = request.form.get('student_list', '').strip()

        # Kolla att vi fick en fil
        if 'docx_file' not in request.files:
            flash("Ingen fil vald!", "error")
            return redirect(url_for('index'))

        file = request.files['docx_file']
        if file.filename == '':
            flash("Inget filnamn!", "error")
            return redirect(url
