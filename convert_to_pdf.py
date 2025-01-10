import os
import subprocess

def convert_docx_to_pdf(input_folder):
    """
    Converts all .docx files in input_folder to .pdf using LibreOffice.

    Args:
        input_folder (str): The path to the folder containing .docx files.

    Returns:
        tuple: (bool, str) where bool indicates success and str contains a message.
    """
    try:
        # Find all DOCX files in the folder
        docx_files = [f for f in os.listdir(input_folder) if f.endswith('.docx')]
        if not docx_files:
            return False, "No DOCX files to convert."

        for docx_file in docx_files:
            docx_path = os.path.join(input_folder, docx_file)  # Full path to the file

            # Run LibreOffice in headless mode to convert to PDF
            subprocess.run([
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                input_folder,
                docx_path
            ], check=True)

        return True, "All files were successfully converted to PDF!"

    except subprocess.CalledProcessError as e:
        return False, f"Conversion error: {e}"

    except Exception as e:
        return False, f"Unexpected error: {e}"

if __name__ == "__main__":
    folder = input("Enter the path to the folder containing .docx files: ")
    if os.path.isdir(folder):
        success, message = convert_docx_to_pdf(folder)
        print(message)
    else:
        print(f"The folder {folder} does not exist!")
