from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = Field(default="local")
    app_version: str = Field(default="0.1.0")
    log_level: str = Field(default="INFO")

    aws_region: str = Field(default="ap-south-1")
    aws_account_id: str = Field(default="123456789012")

    s3_image_bucket: str = Field(default="returniq-images-local")
    s3_presign_expiry_seconds: int = Field(default=300)
    s3_endpoint_url: str | None = Field(default=None)

    dynamodb_table_name: str = Field(default="returniq-main")
    dynamodb_endpoint_url: str | None = Field(default=None)

    step_functions_workflow_arn: str = Field(default="")

    sqs_human_review_queue_url: str = Field(default="")
    sqs_error_queue_url: str = Field(default="")

    sns_buyer_notifications_topic_arn: str = Field(default="")

    sagemaker_endpoint_name: str = Field(default="returniq-return-predictor")

    bedrock_region: str = Field(default="ap-south-1")
    bedrock_model_id: str = Field(default="anthropic.claude-3-haiku-20240307-v1:0")

    rekognition_min_confidence: float = Field(default=60.0)
    rekognition_max_labels: int = Field(default=25)

    grading_confidence_threshold: float = Field(default=87.0)
    fraud_bulk_buy_threshold: int = Field(default=10)
    fraud_window_hours: int = Field(default=72)
    p2p_max_radius_km: float = Field(default=5.0)
    qr_token_ttl_hours: int = Field(default=48)
    expected_images_per_return: int = Field(default=3)

    base_url: str = Field(default="http://localhost:8000")

    @field_validator("grading_confidence_threshold")
    @classmethod
    def validate_confidence_threshold(cls, v: float) -> float:
        if not 0.0 <= v <= 100.0:
            raise ValueError("grading_confidence_threshold must be between 0 and 100")
        return v

    @field_validator("p2p_max_radius_km")
    @classmethod
    def validate_radius(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("p2p_max_radius_km must be positive")
        return v

    @property
    def is_local(self) -> bool:
        return self.app_env == "local"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return AppConfig()
