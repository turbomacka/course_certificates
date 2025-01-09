import os
import pythoncom
import win32com.client

def convert_docx_to_pdf(input_folder):
    """
    Konverterar alla .docx-filer i input_folder till .pdf.
    """
    try:
        # Initiera COM-miljön för tråden
        pythoncom.CoInitialize()

        # Logga alla DOCX-filer som behandlas
        docx_files = [f for f in os.listdir(input_folder) if f.endswith('.docx')]
        if not docx_files:
            return False, "Inga DOCX-filer att konvertera."

        print(f"Konverterar följande DOCX-filer: {docx_files}")

        # Starta Word via win32com
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False

        for docx_file in docx_files:
            docx_path = os.path.abspath(os.path.join(input_folder, docx_file))  # Fullständig sökväg
            pdf_path = docx_path.replace('.docx', '.pdf')

            try:
                # Öppna och spara som PDF
                doc = word.Documents.Open(docx_path)
                doc.SaveAs(pdf_path, FileFormat=17)  # 17 är PDF-format
                doc.Close()
                print(f"Konverterade: {docx_path} -> {pdf_path}")
            except Exception as e:
                print(f"Fel vid konvertering av {docx_file}: {e}")

        word.Quit()
        return True, "Alla filer konverterades till PDF!"

    except Exception as e:
        print(f"Fel vid konvertering: {e}")
        return False, f"Fel vid konvertering: {e}"

    finally:
        # Avsluta COM-miljön
        pythoncom.CoUninitialize()
