from typing import List

from pydantic import BaseModel


class Quarter(BaseModel):
    subject_code: str
    course_number: str
    instr_type: str
    instr_method: str
    section: str
    crn: int
    course_title: str
    meet_time: List[str]
    instructor: str

    class Config:
        orm_mode = True
