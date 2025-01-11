import os
import sys
import subprocess

def convert_docx_to_pdf(folder):
    """
    Converts all .docx files in a folder to .pdf using LibreOffice.
    Returns (success: bool, message: str).
    """
    docx_files = [f for f in os.listdir(folder) if f.endswith('.docx')]
    if not docx_files:
        return False, "No DOCX files found for conversion."

    for docx_file in docx_files:
        docx_path = os.path.join(folder, docx_file)
        pdf_path = os.path.splitext(docx_path)[0] + '.pdf'

        try:
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", docx_path, "--outdir", folder],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            return False, f"Failed to convert {docx_file}: {e.stderr.decode().strip()}"

    return True, "Conversion completed successfully."

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        # Kontrollera LibreOffice-installation
        try:
            result = subprocess.run(["libreoffice", "--version"], capture_output=True, text=True, check=True)
            print(f"LibreOffice version: {result.stdout.strip()}")
        except FileNotFoundError:
            print("LibreOffice is not installed.", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"LibreOffice command failed: {e.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error checking LibreOffice: {e}", file=sys.stderr)
            sys.exit(1)
    elif len(sys.argv) == 2:
        # Kör konvertering
        folder = sys.argv[1]
        success, message = convert_docx_to_pdf(folder)
        if success:
            print(message)
        else:
            print(message, file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python convert_to_pdf.py <folder>")

