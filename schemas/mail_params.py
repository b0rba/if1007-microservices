from datetime import datetime, timezone
from typing import Optional

import pytz
from pydantic import BaseModel, validator


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
