from backend.repositories.profile_repository import (
    ProfileRepository,
)


class ProfileService:

    def __init__(
        self,
        repo: ProfileRepository,
    ):
        self.repo = repo


    def get_profile(
        self,
        user_id: int,
    ):

        return self.repo.get_by_user_id(
            user_id
        )


    def create_profile(
        self,
        user_id: int,
        profile_data: dict,
    ):

        existing_profile = (
            self.repo.get_by_user_id(
                user_id
            )
        )


        if existing_profile:
            return self.repo.update_profile(
                existing_profile,
                profile_data,
            )


        return self.repo.create_profile(
            user_id,
            profile_data,
        )


    def update_profile(
        self,
        user_id: int,
        profile_data: dict,
    ):

        profile = (
            self.repo.get_by_user_id(
                user_id
            )
        )


        if not profile:
            return self.repo.create_profile(
                user_id,
                profile_data,
            )


        return self.repo.update_profile(
            profile,
            profile_data,
        )


    def delete_profile(
        self,
        user_id: int,
    ):

        profile = (
            self.repo.get_by_user_id(
                user_id
            )
        )


        if profile:
            self.repo.delete_profile(
                profile
            )

        return True