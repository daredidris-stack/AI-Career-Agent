from sqlalchemy.orm import Session

from backend.core.time import utc_now
from backend.models.profile import Profile


class ProfileRepository:

    def __init__(self, db: Session):
        self.db = db


    def get_by_user_id(
        self,
        user_id: int,
    ):

        return (
            self.db.query(Profile)
            .filter(Profile.user_id == user_id)
            .first()
        )

    def list_job_search_targets(
        self,
        limit: int = 10,
    ) -> list[tuple[str, str]]:
        target_limit = max(1, limit)
        profiles = (
            self.db.query(Profile)
            .order_by(Profile.updated_at.desc())
            .yield_per(100)
        )
        targets = []
        seen = set()
        for profile in profiles:
            role = str(
                profile.target_role or profile.current_role or ""
            ).strip()
            if not role or role.casefold() in seen:
                continue
            targets.append((role, "Worldwide"))
            seen.add(role.casefold())
            if len(targets) >= target_limit:
                break
        return targets


    def create_profile(
        self,
        user_id: int,
        profile_data: dict,
    ):

        profile = Profile(
            user_id=user_id,
            **profile_data,
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return profile


    def update_profile(
        self,
        profile: Profile,
        profile_data: dict,
    ):

        for key, value in profile_data.items():

            setattr(
                profile,
                key,
                value,
            )

        profile.updated_at = utc_now()

        self.db.commit()
        self.db.refresh(profile)

        return profile


    def delete_profile(
        self,
        profile: Profile,
    ):

        self.db.delete(profile)
        self.db.commit()
