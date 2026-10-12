
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator


class Event(BaseModel):
    event_id: str
    event_time: datetime
    event_type: str
    product_id: int
    category_id: int
    category_code: str | None = None
    brand: str | None = None
    price: Decimal
    user_id: int
    user_session: str

    @field_validator("event_id", mode="before")
    @classmethod
    def normalize_event_id(cls, value: str) -> str:
        if not isinstance(value, str):
            value = str(value) if value is not None else ""

        value = value.strip()

        if not value:
            raise ValueError("Event ID cannot be empty")

        return value

    @field_validator("event_time", mode="before")
    @classmethod
    def normalize_event_time(cls, value):
        if isinstance(value, str) and value.endswith(" UTC"):
            return value[:-4] + "+00:00"

        return value

    @field_validator("event_type", "user_session")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        value = value.strip().lower()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        allowed_types = {
            "view",
            "cart",
            "remove_from_cart",
            "purchase",
        }

        if value not in allowed_types:
            raise ValueError("Unsupported event type")

        return value

    @field_validator("product_id", "user_id")
    @classmethod
    def validate_positive_ids(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ID must be greater than zero")

        return value

    @field_validator("category_id")
    @classmethod
    def validate_category_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Category ID must be greater than zero")

        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("Price cannot be negative")

        return value

    @field_validator("category_code", "brand")
    @classmethod
    def normalize_optional_text(
        cls, value: str | None
    ) -> str | None:
        if value is None or not value.strip():
            return None

        return value.strip().lower()
