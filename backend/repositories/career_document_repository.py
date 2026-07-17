from sqlalchemy.orm import Session

from backend.models.career_document import CareerDocument
from backend.models.career_document_revision import CareerDocumentRevision


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
        self.db.query(CareerDocumentRevision).filter(
            CareerDocumentRevision.document_id == document.id
        ).delete(synchronize_session=False)
        self.db.delete(document)
        self.db.commit()

    def create_revision(self, document: CareerDocument):
        revision = CareerDocumentRevision(
            document_id=document.id,
            user_id=document.user_id,
            title=document.title,
            content=document.content,
        )
        self.db.add(revision)
        self.db.flush()
        return revision

    def list_revisions(self, document_id: int, user_id: int):
        return self.db.query(CareerDocumentRevision).filter(
            CareerDocumentRevision.document_id == document_id,
            CareerDocumentRevision.user_id == user_id,
        ).order_by(CareerDocumentRevision.created_at.desc()).all()

    def get_revision(
        self,
        revision_id: int,
        document_id: int,
        user_id: int,
    ):
        return self.db.query(CareerDocumentRevision).filter(
            CareerDocumentRevision.id == revision_id,
            CareerDocumentRevision.document_id == document_id,
            CareerDocumentRevision.user_id == user_id,
        ).first()
