# Certificate Generator

## Overview
Certificate Generator is a Python-based web application designed to simplify the creation of personalized certificates. Users can upload a Word template with placeholders, generate certificates dynamically, and convert them to PDFs. The app is ideal for educators, event organizers, and anyone needing batch certificate generation.

---

## Features
- **Dynamic Text Replacement**: Replace placeholders like `NAMN` and `DATUM` in Word templates.
- **Batch Processing**: Generate certificates for multiple recipients using a single template and list of names.
- **PDF Conversion**: Convert DOCX certificates to PDF using LibreOffice in headless mode.
- **Progress Tracking**: Real-time progress updates during PDF conversion with humorous messages.
- **ZIP Downloads**: Download all generated DOCX or PDF files as a ZIP archive.

---

## Prerequisites
- **Python Version**: Python 3.8 or later.
- **Dependencies**: Install via `requirements.txt`.
- **LibreOffice**: Required for DOCX-to-PDF conversion.

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/turbomacka/certificate-generator.git
   cd certificate-generator
Set up a virtual environment:

bash
Kopiera kod
python3 -m venv venv
source venv/bin/activate  # For Linux/MacOS
venv\Scripts\activate     # For Windows
Install required dependencies:

bash
Kopiera kod
pip install -r requirements.txt
Verify LibreOffice installation:

bash
Kopiera kod
libreoffice --version
Usage
Start the Application:

bash
Kopiera kod
python app.py
Access the Web Interface: Open your browser and navigate to http://127.0.0.1:5000.

Upload Template and Enter Data:

Upload a Word template containing NAMN and DATUM placeholders.
Enter course code, date, and names (one per line).
Generate and Download Certificates:

Generate DOCX certificates.
Convert to PDF and download individual files or ZIP archives.
Project Structure
app.py: Main application logic using Flask.
convert_to_pdf.py: Handles DOCX-to-PDF conversion using LibreOffice.
templates/: Contains HTML templates for the web interface (index.html, done.html, progress.html).
uploads/: Directory where generated files are temporarily stored.
cert_template/: Directory for storing uploaded Word templates.
Example Workflow
Upload a Word template with placeholders.
Enter necessary data (e.g., names, course codes, dates).
Generate certificates in DOCX format.
Convert to PDF and download as needed.
Author
Created by Turbomacka. For inquiries or suggestions, feel free to contact the author through GitHub.

Contributions
Contributions, issues, and feature requests are welcome. Please fork the repository, make changes, and submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for more details.

Notes
Ensure your Word template uses simple, compatible formatting to maintain fidelity during PDF conversion.
LibreOffice must be installed and added to the system path for PDF conversion to work.