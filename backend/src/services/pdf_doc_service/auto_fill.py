import sys
import os
# Add user site-packages explicitly due to environment mismatch
sys.path.append(r"C:\Users\rubas\AppData\Roaming\Python\Python311\site-packages")
from fillpdf.fillpdfs import write_fillable_pdf, get_form_fields

def fill_pdf_form(input_pdf: str, output_pdf: str, form_data: dict):
    if not os.path.exists(input_pdf):
        print(f"Error: {input_pdf} not found.")
        return

    try:
        print(f"Inspecting fields in {input_pdf}...")
        try:
            fields = get_form_fields(input_pdf)
            print("Found fields:")
            for key, value in fields.items():
                print(f" - {key}: {value}")
        except Exception as e:
             print(f"Warning: Could not inspect fields (pdftk missing?): {e}")

        print(f"Filling {input_pdf} using fillpdf...")
        write_fillable_pdf(input_pdf, output_pdf, form_data)
        print(f"Successfully filled {input_pdf} and saved to {output_pdf}")
        return output_pdf
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Note: fillpdf requires pdftk to be installed and in your system PATH.")
        raise e

if __name__ == "__main__":
    # Example usage
    sample_data = {
        "Given Name Text Box": "Rubyy",
        "Family Name Text Box": "S",
        "Address 1 Text Box": "123 Main St",
        "House nr Text Box": "42",
        "Country Combo Box": "India",
        "Gender List Box": "women",
        "Height Formatted Field": "180",
        "City Text Box": "Chennai",
        "Driving License Check Box": "Yes", 
        "Favourite Colour List Box": "Blue",
        "Language 1 Check Box": "Yes"
    }
    fill_pdf_form("sample3.pdf", "filled_form.pdf", sample_data)
