from sqlalchemy.orm import Session

from backend.models.career_document import CareerDocument


class CareerDocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(
        self,
        user_id: int,
        kind: str | None = None,
    ) -> list[CareerDocument]:
        query = self.db.query(CareerDocument).filter(
            CareerDocument.user_id == user_id
        )
        if kind:
            query = query.filter(CareerDocument.kind == kind)
        return query.order_by(CareerDocument.updated_at.desc()).all()

    def get_for_user(
        self,
        document_id: int,
        user_id: int,
    ) -> CareerDocument | None:
        return self.db.query(CareerDocument).filter(
            CareerDocument.id == document_id,
            CareerDocument.user_id == user_id,
        ).first()

    def create(self, **values) -> CareerDocument:
        document = CareerDocument(**values)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def save(self, document: CareerDocument) -> CareerDocument:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: CareerDocument) -> None:
        self.db.delete(document)
        self.db.commit()
