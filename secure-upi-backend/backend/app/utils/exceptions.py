"""
Thin helpers so services raise consistent, well-documented HTTP errors
instead of ad-hoc HTTPException calls scattered around the codebase.
"""
from fastapi import HTTPException, status


def duplicate_email() -> HTTPException:
    return HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")


def invalid_credentials() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")


def not_found(resource: str = "Resource") -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{resource} not found")


def bad_request(message: str) -> HTTPException:
    return HTTPException(status.HTTP_400_BAD_REQUEST, message)


def model_unavailable() -> HTTPException:
    return HTTPException(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        "The fraud-detection model is not loaded yet. Train the ML pipeline "
        "and run scripts/copy_ml_artifacts.py, then restart the API.",
    )
