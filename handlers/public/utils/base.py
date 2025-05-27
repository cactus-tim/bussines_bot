"""
Handlers utils
"""

# --------------------------------------------------------------------------------

from database.req import (
    get_user, create_user
)
# --------------------------------------------------------------------------------

async def create_user_if_not_exists(user_id: int, username: str, first_contact: str = None) -> str:
    """
    Create a user if not exists.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        first_contact (str, optional): Referrer or first hash source.

    Returns:
        str: User status or existing user object.
    """
    user = await get_user(user_id)
    if user == "not created":
        user_data = {'handler': username}
        if first_contact:
            user_data['first_contact'] = first_contact
        await create_user(user_id, user_data)
    return user
