"""Bot States.
State machine definitions for various bot workflows and forms.
"""

# --------------------------------------------------------------------------------

from aiogram.fsm.state import StatesGroup, State

# --------------------------------------------------------------------------------

class Questionnaire(StatesGroup):
    """Questionnaire form states for user registration.

    Args:
        None

    Returns:
        None
    """
    full_name = State()
    degree = State()
    course = State()
    program = State()
    email = State()
    vacancy = State()
    motivation = State()
    plans = State()
    strengths = State()
    career_goals = State()
    team_motivation = State()
    role_in_team = State()
    events = State()
    found_info = State()
    resume = State()
    another_vacancy = State()

# --------------------------------------------------------------------------------

class EventReg(StatesGroup):
    """Event registration form states.

    Args:
        None

    Returns:
        None
    """
    waiting_name = State()
    waiting_surname = State()
    waiting_fathername = State()
    waiting_mail = State()
    waiting_phone = State()
    waiting_org = State()

# --------------------------------------------------------------------------------

class EventCreateState(StatesGroup):
    """Event creation form states.

    Args:
        None

    Returns:
        None
    """
    waiting_event_name = State()
    waiting_event_date = State()
    waiting_event_time = State()
    waiting_event_place = State()
    waiting_links_count = State()

# --------------------------------------------------------------------------------

class EventState(StatesGroup):
    """Event management states.

    Args:
        None

    Returns:
        None
    """
    waiting_ev = State()
    waiting_ev_for_link = State()
    waiting_links_count = State()

# --------------------------------------------------------------------------------

class VacancyState(StatesGroup):
    """Vacancy management states.

    Args:
        None

    Returns:
        None
    """
    waiting_for_vacancy_name = State()
    waiting_for_vacancy_name_to_delete = State()

# --------------------------------------------------------------------------------

class PostState(StatesGroup):
    """Post creation and management states.

    Args:
        None

    Returns:
        None
    """
    waiting_for_post_to_all_text1 = State()
    waiting_for_post_to_all_text05 = State()
    waiting_for_post_to_all_text = State()
    waiting_for_post_to_ev_ev_unreg = State()
    waiting_for_post_to_all_text1_unreg = State()
    waiting_for_post_to_all_text05_unreg = State()
    waiting_for_post_to_all_text_unreg = State()
    waiting_for_post_to_ev_ev = State()
    waiting_for_post_to_ev_text = State()
    waiting_for_post_wth_op_to_ev_ev = State()
    waiting_for_post_wth_op_to_ev_text = State()
    waiting_for_post_to_all_media = State()
    waiting_for_post_to_ev_media = State()
    waiting_for_post_to_all_media_unreg = State()

# --------------------------------------------------------------------------------

class StatState(StatesGroup):
    """Statistics management states.

    Args:
        None

    Returns:
        None
    """
    waiting_for_ev = State()
    waiting_for_give_away_ev = State()
    waiting_user_id = State()
    waiting_for_ev1 = State()
    waiting_for_ev2 = State()

# --------------------------------------------------------------------------------

class WinnerState(StatesGroup):
    """Winner selection states.

    Args:
        None

    Returns:
        None
    """
    wait_give_away_event = State()
    wait_give_away_id = State()

# --------------------------------------------------------------------------------

class GiveAwayState(StatesGroup):
    """Giveaway management states.

    Args:
        None

    Returns:
        None
    """
    waiting_event = State()
    waiting_org_name = State()
    waiting_id = State()