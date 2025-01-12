import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

def convert_single_file(docx_path, folder):
    """
    Converts a single .docx file to .pdf using LibreOffice.
    """
    pdf_path = os.path.splitext(docx_path)[0] + '.pdf'
    try:
        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", docx_path, "--outdir", folder],
            check=True,
            capture_output=True
        )
        return True, f"Converted: {os.path.basename(docx_path)}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to convert {os.path.basename(docx_path)}: {e.stderr.decode().strip()}"

def parallel_convert_docx_to_pdf(folder, max_workers=4):
    """
    Converts all .docx files in a folder to .pdf using LibreOffice in parallel.
    """
    docx_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.docx')]
    if not docx_files:
        return False, "No DOCX files found for conversion."

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(convert_single_file, docx, folder): docx for docx in docx_files}
        for future in futures:
            success, message = future.result()
            results.append((success, message))
            print(message)

    failed_files = [msg for success, msg in results if not success]
    if failed_files:
        return False, f"Some files failed to convert: {', '.join(failed_files)}"
    return True, "All files converted successfully."

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        try:
            # Kontrollera LibreOffice
            which_result = subprocess.run(["which", "libreoffice"], capture_output=True, text=True, check=True)
            print(f"LibreOffice binary path: {which_result.stdout.strip()}")

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
        folder = sys.argv[1]
        success, message = parallel_convert_docx_to_pdf(folder)
        if success:
            print(message)
        else:
            print(message, file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: python convert_to_pdf.py <folder>")
