from enum import Enum


class Template(Enum):
    CONFIRMATION_TO_MENTOR = 7
    CONFIRMATION_TO_MENTORED = 9
    NOTIFY_SUBSCRIBED_USERS_NOT_SELECTED = 10
    NOTIFY_SUBSCRIBED_USERS_MENTORING_CANCELED = 11
    NOTIFY_MENTOR_OF_MENTORED_LEAVING = 16
