from __future__ import annotations


class ReturnIQError(Exception):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class DomainValidationError(ReturnIQError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="DOMAIN_VALIDATION_ERROR")


class EntityNotFoundError(ReturnIQError):
    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(
            message=f"{entity} with identifier '{identifier}' not found",
            code="ENTITY_NOT_FOUND",
        )
        self.entity = entity
        self.identifier = identifier


class InvalidStateTransitionError(ReturnIQError):
    def __init__(self, entity: str, current: str, attempted: str) -> None:
        super().__init__(
            message=f"{entity} cannot transition from '{current}' to '{attempted}'",
            code="INVALID_STATE_TRANSITION",
        )
        self.entity = entity
        self.current = current
        self.attempted = attempted


class ConfidenceBelowThresholdError(ReturnIQError):
    def __init__(self, confidence: float, threshold: float) -> None:
        super().__init__(
            message=f"Confidence {confidence:.1f}% is below threshold {threshold:.1f}%",
            code="CONFIDENCE_BELOW_THRESHOLD",
        )
        self.confidence = confidence
        self.threshold = threshold


class FraudFlaggedError(ReturnIQError):
    def __init__(self, reason: str) -> None:
        super().__init__(message=reason, code="FRAUD_FLAGGED")


class QRTokenAlreadyScannedError(ReturnIQError):
    def __init__(self, qr_token: str) -> None:
        super().__init__(
            message=f"QR token '{qr_token}' has already been scanned — possible tampering",
            code="QR_ALREADY_SCANNED",
        )
        self.qr_token = qr_token


class QRTokenNotFoundError(ReturnIQError):
    def __init__(self, qr_token: str) -> None:
        super().__init__(
            message=f"QR token '{qr_token}' not found",
            code="QR_TOKEN_NOT_FOUND",
        )


class ImageUploadError(ReturnIQError):
    def __init__(self, reason: str) -> None:
        super().__init__(message=reason, code="IMAGE_UPLOAD_ERROR")


class InfrastructureError(ReturnIQError):
    def __init__(self, service: str, reason: str) -> None:
        super().__init__(
            message=f"{service} operation failed: {reason}",
            code="INFRASTRUCTURE_ERROR",
        )
        self.service = service


class WorkflowTriggerError(ReturnIQError):
    def __init__(self, return_id: str, reason: str) -> None:
        super().__init__(
            message=f"Failed to start workflow for return '{return_id}': {reason}",
            code="WORKFLOW_TRIGGER_ERROR",
        )