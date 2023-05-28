import io
from collections.abc import Callable
from typing import Final

import pandas as pd

from api_gateway.utility.file_type.file_type import FileType

_DATAFRAME_READER: Final[dict[FileType, Callable[[io.BytesIO], pd.DataFrame]]] = {
    FileType.CSV: pd.read_csv,
    FileType.XLSX: lambda bytes_io: pd.read_excel(bytes_io, engine="openpyxl"),
}


def file_to_dataframe(file_content: bytes, file_type: FileType) -> pd.DataFrame:
    dataframe_reader = _DATAFRAME_READER[file_type]
    with io.BytesIO(file_content) as bytes_io:
        return dataframe_reader(bytes_io)
