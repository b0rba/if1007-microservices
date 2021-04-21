from datetime import datetime, timezone
from typing import Optional

import pytz
from pydantic import BaseModel, validator, EmailStr

TIMEZONE = 'America/Recife'


class MailParams(BaseModel):
    mentor_name: str
    mentoring_datetime: datetime
    mentored_name: Optional[str]
    mentor_id: Optional[str]
    mentored_id: Optional[str]

    @validator('mentoring_datetime')
    def set_timezone(cls, v):
        if v:
            return v.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone(TIMEZONE))


class ConfirmationToMentorParams(BaseModel):
    mentoring_datetime: datetime
    mentor_name: str
    mentored_name: str
    mentored_id: str
    mentor_email: EmailStr


class ConfirmationToMentoredParams(BaseModel):
    mentoring_datetime: datetime
    mentor_name: str
    mentored_name: str
    mentor_id: str
    mentored_email: EmailStr


class NotifySubscribedUserNotSelectedParams(BaseModel):
    mentoring_datetime: datetime
    mentor_name: str
    mentored_name: str
    mentored_email: EmailStr


class NotifySubscribedUserMentoringCanceledParams(BaseModel):
    mentoring_datetime: datetime
    mentor_name: str
    mentored_name: str
    mentored_email: EmailStr


class NotifyMentorOfMentoredLeavingParams(BaseModel):
    mentoring_datetime: datetime
    mentor_name: str
    mentored_name: str
    mentored_id: str
    mentor_email: EmailStr
