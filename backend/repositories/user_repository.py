from sqlalchemy.orm import Session

from backend.models.user import User


class UserRepository:

    def __init__(self, db: Session):
        self.db = db


    def get_by_email(self, email: str):

        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )


    def create_user(
        self,
        email: str,
        password_hash: str,
    ):

        user = User(
            email=email,
            password_hash=password_hash,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user


    def get_by_id(self, user_id: int):

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )