"""
Bot Config
Configuration for bot parameters.
"""


# --------------------------------------------------------------------------------
class BotConfig:
    """
    Configuration holder for bot settings.

    Args:
        admin_ids (list[int] | None): List of administrator user IDs.
        welcome_message (str | None): Welcome message for new users.
    """

    def __init__(self, admin_ids: list[int] | None = None, welcome_message: str | None = None):
        """
        Initialize BotConfig with admin IDs and welcome message.

        Args:
            admin_ids (list[int] | None): Administrator user IDs.
            welcome_message (str | None): Welcome message text.
        """
        self.admin_ids = admin_ids
        self.welcome_message = welcome_message
