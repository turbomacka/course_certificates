import os
import sys
import subprocess

def convert_docx_to_pdf(folder):
    """
    Converts all .docx files in a folder to .pdf using LibreOffice.
    Returns (success: bool, message: str).
    """
    try:
        # Kontrollera skrivbehörigheter
        test_file = os.path.join(folder, "test_write.txt")
        with open(test_file, "w") as f:
            f.write("Test file for permissions")
        os.remove(test_file)
    except Exception as e:
        return False, f"Folder permissions error: {e}"

    docx_files = [f for f in os.listdir(folder) if f.endswith('.docx')]
    if not docx_files:
        return False, "No DOCX files found for conversion."

    for docx_file in docx_files:
        docx_path = os.path.join(folder, docx_file)
        try:
            result = subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", docx_path, "--outdir", folder],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Conversion output for {docx_file}: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            return False, f"Failed to convert {docx_file}: {e.stderr.strip()}"
        except Exception as e:
            return False, f"Unexpected error converting {docx_file}: {e}"

    return True, "Conversion completed successfully."

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        try:
            # Kontrollera var LibreOffice finns
            which_result = subprocess.run(["which", "libreoffice"], capture_output=True, text=True, check=True)
            print(f"LibreOffice binary path: {which_result.stdout.strip()}")

            # Kontrollera LibreOffice-versionen
            version_result = subprocess.run(["libreoffice", "--version"], capture_output=True, text=True, check=True)
            print(f"LibreOffice version: {version_result.stdout.strip()}")
        except FileNotFoundError:
            print("LibreOffice is not installed or not in PATH.", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"LibreOffice command failed (stdout): {e.stdout.strip()}", file=sys.stderr)
            print(f"LibreOffice command failed (stderr): {e.stderr.strip()}", file=sys.stderr)
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
