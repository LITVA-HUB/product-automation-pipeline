from __future__ import annotations

from sqlalchemy.orm import Session

from app.adapters.repositories.models import IntakeEventRow
from app.services.intake.service import IntakeItem
from app.services.telegram.intake import IntakeEvent


class IntakeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, event: IntakeEvent) -> IntakeEventRow:
        row = IntakeEventRow(
            id=str(event.id),
            source=event.source,
            operator_id=event.operator_id,
            chat_id=event.chat_id,
            kind=event.item.kind,
            payload=event.item.payload,
            raw_update=event.raw_update,
            status=event.status,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def list_pending(self, limit: int = 100) -> list[IntakeEventRow]:
        return (
            self.session.query(IntakeEventRow)
            .filter(IntakeEventRow.status == "pending")
            .order_by(IntakeEventRow.created_at.asc(), IntakeEventRow.id.asc())
            .limit(limit)
            .all()
        )


def row_to_event(row: IntakeEventRow) -> IntakeEvent:
    return IntakeEvent(
        id=row.id,
        source=row.source,
        operator_id=row.operator_id,
        chat_id=row.chat_id,
        item=IntakeItem(kind=row.kind, payload=row.payload),
        raw_update=row.raw_update,
        status=row.status,
    )
