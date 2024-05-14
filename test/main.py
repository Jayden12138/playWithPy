import os
import glob
from pdf_utils import extract_tables_from_pdf
from excel_utils import fill_excel_with_data

def process_pdfs_in_folder(folder_path):
    pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))

    for pdf_file in pdf_files:
        table_df, total_amount = extract_tables_from_pdf(pdf_file)

        if not table_df.empty and total_amount is not None:
            excel_path = 'target.xlsx'
            fill_excel_with_data(excel_path, table_df, total_amount)


if __name__ == "__main__":
    pdf_folder = 'pdf_folder'
    process_pdfs_in_folder(pdf_folder)
