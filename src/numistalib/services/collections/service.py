"""Collection service implementation."""

from collections.abc import Mapping
from datetime import date
from typing import Any
from typing import cast
from typing import Literal
from typing import TypeAlias

from pydantic import ValidationError

from numistalib.client import AsyncClientProtocol
from numistalib.client import SyncClientProtocol
from numistalib.models import UserCollection as UserCollectionModel
from numistalib.models.collections import CollectedItem
from numistalib.models.collections import GradingDetails, TypeDetail
from numistalib.models.types import TypeFull
from numistalib.services.collections.base import CollectionServiceBase

CollectedItemGrade: TypeAlias = Literal["g", "vg", "f", "vf", "xf", "au", "unc"]
_ALLOWED_GRADES: frozenset[str] = frozenset({"g", "vg", "f", "vf", "xf", "au", "unc"})


def _coerce_grade(value: object) -> CollectedItemGrade | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None

    normalized = value.strip().lower()
    if normalized in _ALLOWED_GRADES:
        return cast(CollectedItemGrade, normalized)

    return None


def _coerce_grading_details(value: object) -> GradingDetails | None:
    if value is None:
        return None

    try:
        model_validate = getattr(GradingDetails, "model_validate", None)
        if callable(model_validate):
            return cast(GradingDetails, model_validate(value))
        # Pydantic v1 fallback
        parse_obj = getattr(GradingDetails, "parse_obj", None)
        if callable(parse_obj):
            return cast(GradingDetails, parse_obj(value))
    except (TypeError, ValidationError):
        return None

    return None


class CollectionService(CollectionServiceBase):
    """Unified collection service supporting both sync and async clients.

    Requires OAuth authentication with appropriate scopes.
    """

    def __init__(self, client: SyncClientProtocol | AsyncClientProtocol) -> None:
        """Initialize collection service.

        Parameters
        ----------
        client : SyncClientProtocol | AsyncClientProtocol
            HTTP client instance (sync or async)
        """
        super().__init__(client)

    def to_models(
        self, items: list[Mapping[str, Any]], user_id: int | None = None, **kwargs: Any  # noqa: ARG002
    ) -> list[CollectedItem]:
        """Convert API response items to CollectedItem models.

        Parameters
        ----------
        items : list[Mapping[str, Any]]
            Raw API response items
        user_id : int | None
            Associated user ID (required)
        **kwargs : Any
            Additional context

        Returns
        -------
        list[CollectedItem]
            Parsed collected item models
        """
        if user_id is None:
            raise ValueError("user_id is required for collection conversion")

        collected_items: list[CollectedItem] = []
        for item in items:
            type_info = TypeDetail(**cast(dict[str, Any], item["type"]))
            issue_info = cast(Mapping[str, Any] | None, item.get("issue"))
            price_info = cast(Mapping[str, Any] | None, item.get("price"))

            collected_items.append(
                CollectedItem(
                    id=cast(int, item["id"]),
                    type=type_info,
                    issue=dict(issue_info) if issue_info is not None else None,
                    private_comment=cast(str | None, item.get("private_comment")),
                    public_comment=cast(str | None, item.get("public_comment")),
                    price=dict(price_info) if price_info is not None else None,
                    collection=(
                        UserCollectionModel(**cast(dict[str, Any], item["collection"]))
                        if item.get("collection") is not None
                        else None
                    ),
                    pictures=cast(list | None, item.get("pictures")),
                    quantity=cast(int, item.get("quantity", 1)),
                    grade=_coerce_grade(item.get("grade")),
                    for_swap=bool(item.get("for_swap", False)),
                    acquisition_date=cast(date | None, item.get("acquisition_date")),
                    acquisition_place=cast(str | None, item.get("acquisition_place")),
                    serial_number=cast(str | None, item.get("serial_number")),
                    internal_id=cast(str | None, item.get("internal_id")),
                    storage_location=cast(str | None, item.get("storage_location")),
                    weight=cast(float | None, item.get("weight")),
                    size=cast(float | None, item.get("size")),
                    axis=cast(int | None, item.get("axis")),
                    grading_details=_coerce_grading_details(item.get("grading_details")),
                )
            )
        return collected_items