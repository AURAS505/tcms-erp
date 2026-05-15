from rest_framework import status

from common.responses import api_error, api_success, validation_error_response


def test_api_success_matches_response_envelope():
    response = api_success({"id": "1"}, message="Created", meta={"source": "test"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "success": True,
        "data": {"id": "1"},
        "message": "Created",
        "errors": None,
        "meta": {"source": "test"},
    }


def test_api_error_matches_response_envelope():
    response = api_error(message="Failed", errors={"field": ["Invalid"]})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert response.data["errors"] == {"field": ["Invalid"]}


def test_validation_error_response_uses_standard_message():
    response = validation_error_response({"name": ["Required"]})

    assert response.data["message"] == "Validation failed"
    assert response.data["errors"] == {"name": ["Required"]}
