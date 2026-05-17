from io import BytesIO

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

from common.validators import (
    get_allowed_upload_extensions,
    get_max_upload_size_bytes,
    secure_upload_path,
    validate_upload_extension,
    validate_upload_size,
    validate_uploaded_document,
)


class UploadStub(BytesIO):
    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name
        self.size = len(content)


@override_settings(ALLOWED_UPLOAD_EXTENSIONS=["pdf", "jpg"])
def test_configured_allowed_upload_extensions_are_normalized():
    assert get_allowed_upload_extensions() == {"pdf", "jpg"}


@override_settings(MAX_UPLOAD_SIZE_BYTES=2048)
def test_configured_max_upload_size_is_used():
    assert get_max_upload_size_bytes() == 2048


def test_allowed_extension_passes():
    assert validate_upload_extension("Student-Marksheet.PDF", allowed_extensions={"pdf"}) == "pdf"


def test_disallowed_extension_fails():
    with pytest.raises(ValidationError, match="Unsupported file extension"):
        validate_upload_extension("script.exe", allowed_extensions={"pdf", "png"})


def test_missing_extension_fails():
    with pytest.raises(ValidationError, match="must have an extension"):
        validate_upload_extension("passport", allowed_extensions={"pdf"})


def test_file_larger_than_max_size_fails():
    upload = UploadStub(b"abc", "document.pdf")

    with pytest.raises(ValidationError, match="too large"):
        validate_upload_size(upload, max_size=2)


def test_uploaded_document_validates_name_and_size():
    upload = UploadStub(b"ab", "photo.jpg")

    validate_uploaded_document(upload, allowed_extensions={"jpg"}, max_size=2)


def test_secure_upload_path_does_not_use_raw_original_filename():
    path = secure_upload_path("students", "birth certificate", "My Passport.pdf")

    assert path.startswith("private/students/birth-certificate/")
    assert path.endswith(".pdf")
    assert "My Passport" not in path
