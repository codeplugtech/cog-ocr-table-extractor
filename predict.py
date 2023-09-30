import pathlib
import tempfile

from cog import BasePredictor, Input, Path
from img2table.document import Image
from img2table.document import PDF
from img2table.ocr import EasyOCR
import pandas as pd


class Predictor(BasePredictor):
    def predict(
            self,
            page_num: int = Input(description="Specify Pdf Pages", default=None),
            merge_table: bool = Input(description="Merge All tables", default=True),
            file_path: Path = Input(description="Input file", default=None)
    ) -> Path:

        if file_path is None:
            raise ValueError('Pdf/Img file path required')

        file_extension = pathlib.Path(file_path).suffix.strip().lower()

        print("File extension:", file_extension)

        if not file_extension.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.pdf')):
            raise ValueError('Provide valid file extension')

        ocr = EasyOCR(
            lang=["en"])

        print("Page number:", page_num)

        match file_extension:
            case ".pdf":
                print("Processing Pdf file")
                doc = PDF(file_path.read_bytes(), pages=list(
                    range(0, (page_num - 1) + 1)) if page_num is not None else [])  # Pass the page_num as a list
            case _:
                print("Processing Image file: ", file_extension)
                doc = Image(file_path.read_bytes(), detect_rotation=True)

        print('Temp folder with Excel path created')
        output_path = Path(tempfile.mkdtemp()) / "excel.xlsx"

        if merge_table:
            print("Merging all Tables into Single excel file")
            extracted_tables = doc.extract_tables(ocr=ocr, implicit_rows=True, borderless_tables=True,
                                                  min_confidence=60)
            data_list: [] = []

            for key, table_list in extracted_tables.items():
                for table in table_list:
                    data_list.append(table.df)

            df: pd.DataFrame() = pd.concat(data_list, ignore_index=True)
            df.to_excel(output_path, index=True)

        else:
            print('Converting to Excel')
            doc.to_xlsx(dest=output_path, ocr=ocr, implicit_rows=True, borderless_tables=True,
                        min_confidence=50)

        return Path(output_path)
