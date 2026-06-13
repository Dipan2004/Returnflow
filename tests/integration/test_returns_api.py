from __future__ import annotations

import boto3
from fastapi.testclient import TestClient

from app.config import get_config


def _upload_fake_image(bucket: str, key: str, region: str) -> None:
    s3 = boto3.client("s3", region_name=region)
    s3.put_object(Bucket=bucket, Key=key, Body=b"fake-image-bytes", ContentType="image/jpeg")


def test_create_return_returns_presigned_upload_urls(client: TestClient) -> None:
    response = client.post(
        "/returns",
        json={
            "sku_id": "B08N5WRWNW",
            "seller_id": "seller_xyz",
            "buyer_id": "buyer_abc",
            "image_count": 3,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "AWAITING_IMAGES"
    assert len(body["upload_urls"]) == 3
    for upload_url in body["upload_urls"]:
        assert upload_url["key"].startswith(f"pending/{body['return_id']}/")
        assert upload_url["url"]


def test_get_return_returns_full_detail(client: TestClient) -> None:
    create_response = client.post(
        "/returns",
        json={
            "sku_id": "SKU-1",
            "seller_id": "seller_1",
            "buyer_id": "buyer_1",
            "image_count": 3,
        },
    )
    return_id = create_response.json()["return_id"]

    response = client.get(f"/returns/{return_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["return_id"] == return_id
    assert body["sku_id"] == "SKU-1"
    assert body["status"] == "AWAITING_IMAGES"
    assert body["image_keys"] == []


def test_get_return_status(client: TestClient) -> None:
    create_response = client.post(
        "/returns",
        json={
            "sku_id": "SKU-2",
            "seller_id": "seller_2",
            "buyer_id": "buyer_2",
            "image_count": 2,
        },
    )
    return_id = create_response.json()["return_id"]

    response = client.get(f"/returns/{return_id}/status")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "AWAITING_IMAGES"
    assert body["image_count"] == 0
    assert body["expected_image_count"] == 2


def test_complete_image_upload_transitions_status(client: TestClient) -> None:
    config = get_config()

    create_response = client.post(
        "/returns",
        json={
            "sku_id": "SKU-3",
            "seller_id": "seller_3",
            "buyer_id": "buyer_3",
            "image_count": 2,
        },
    )
    body = create_response.json()
    return_id = body["return_id"]
    keys = [u["key"] for u in body["upload_urls"]]

    for key in keys:
        _upload_fake_image(config.s3_image_bucket, key, config.aws_region)

    response = client.post(
        f"/returns/{return_id}/images/complete",
        json={"image_keys": keys},
    )

    assert response.status_code == 200
    completion_body = response.json()
    assert completion_body["status"] == "IMAGES_RECEIVED"
    assert completion_body["image_count"] == 2
    assert completion_body["all_images_received"] is True

    status_response = client.get(f"/returns/{return_id}/status")
    assert status_response.json()["status"] == "IMAGES_RECEIVED"


def test_complete_image_upload_rejects_key_not_uploaded(client: TestClient) -> None:
    create_response = client.post(
        "/returns",
        json={
            "sku_id": "SKU-4",
            "seller_id": "seller_4",
            "buyer_id": "buyer_4",
            "image_count": 1,
        },
    )
    body = create_response.json()
    return_id = body["return_id"]
    key = body["upload_urls"][0]["key"]

    response = client.post(
        f"/returns/{return_id}/images/complete",
        json={"image_keys": [key]},
    )

    assert response.status_code == 422


def test_get_return_returns_404_for_unknown_id(client: TestClient) -> None:
    from app.domain.value_objects.return_id import ReturnId

    unknown_id = ReturnId.generate().value
    response = client.get(f"/returns/{unknown_id}")

    assert response.status_code == 404


def test_create_return_validates_payload(client: TestClient) -> None:
    response = client.post(
        "/returns",
        json={"sku_id": "", "seller_id": "seller_1", "buyer_id": "buyer_1"},
    )

    assert response.status_code == 422
