import os
import sys
import subprocess

LIBREOFFICE_PATH = "/usr/bin/libreoffice"  # Uppdatera med rätt sökväg från loggarna

def convert_docx_to_pdf(folder):
    """
    Converts all .docx files in a folder to .pdf using LibreOffice.
    """
    docx_files = [f for f in os.listdir(folder) if f.endswith('.docx')]
    if not docx_files:
        return False, "No DOCX files found for conversion."

    for docx_file in docx_files:
        docx_path = os.path.join(folder, docx_file)
        try:
            result = subprocess.run(
                [LIBREOFFICE_PATH, "--headless", "--convert-to", "pdf", docx_path, "--outdir", folder],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Conversion succeeded for {docx_file}: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"Error converting {docx_file} (stdout): {e.stdout.strip()}", file=sys.stderr)
            print(f"Error converting {docx_file} (stderr): {e.stderr.strip()}", file=sys.stderr)
            return False, f"Failed to convert {docx_file}: {e.stderr.strip()}"
        except Exception as e:
            print(f"Unexpected error converting {docx_file}: {e}", file=sys.stderr)
            return False, f"Unexpected error converting {docx_file}: {e}"

    return True, "Conversion completed successfully."

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        try:
            # Testa var LibreOffice finns
            which_result = subprocess.run(["which", "libreoffice"], capture_output=True, text=True, check=True)
            print(f"LibreOffice binary path: {which_result.stdout.strip()}")

            # Försök starta LibreOffice utan konvertering
            test_command = subprocess.run(
                ["libreoffice", "--headless", "--version"],
                capture_output=True,
                text=True
            )
            if test_command.returncode != 0:
                print(f"LibreOffice version check failed (stdout): {test_command.stdout.strip()}", file=sys.stderr)
                print(f"LibreOffice version check failed (stderr): {test_command.stderr.strip()}", file=sys.stderr)
                sys.exit(1)
            print(f"LibreOffice version: {test_command.stdout.strip()}")
        except FileNotFoundError:
            print("LibreOffice is not installed or not in PATH.", file=sys.stderr)
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
