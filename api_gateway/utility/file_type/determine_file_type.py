from magic import Magic

from api_gateway.utility.file_type.exceptions import UnsupportedFileTypeException
from api_gateway.utility.file_type.file_type import FileType


def determine_file_type(file_content: bytes) -> FileType:
    mime = Magic(mime=True)
    file_type = mime.from_buffer(file_content)

    if file_type == "text/csv":
        return FileType.CSV

    if file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return FileType.XLSX

    raise UnsupportedFileTypeException("Unsupported file type")
