"""
Keyboard layouts package.
"""

from keyboards.club_events.admin.admin_keyboards import *
from keyboards.club_events.common import *
from keyboards.club_events.event.event_keyboards import *
from keyboards.club_events.face_control.face_control_keyboards import *
from keyboards.quest.quest_keyboards import *
from .base import main_reply_keyboard

__all__ = [
    # Common utils
    'make_k_from_list',

    # Common keyboards
    'main_reply_keyboard',
    'link_ikb',
    'yes_no_ikb',
    'yes_no_hse_ikb',
    'yes_no_link_ikb',
    'unreg_yes_no_link_ikb',

    # Event keyboards
    'vacancy_selection_keyboard',
    'another_vacancy_keyboard',
    'events_ikb',
    'get_ref_ikb',
    'choose_event_for_qr',

    # Admin keyboards
    'post_target',
    'post_ev_target',
    'stat_target',
    'apply_winner',
    'top_ikb',

    # Face control keyboards
    'face_checkout_kb',
    'back_to_face_control',
    'face_control_menu_kb',
    'face_controls_list',
    'yes_no_face',

    # Quest keyboards
    'quest_keyboard_1',
    'quest_keyboard_2',
]
