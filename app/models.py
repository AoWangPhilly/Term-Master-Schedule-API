from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY

from .database import Base


class Quarter(Base):
    __tablename__ = "quarters"

    subject_code = Column(String, nullable=False)
    course_number = Column(Integer, nullable=False)
    instr_type = Column(String, nullable=False)
    instr_method = Column(String, nullable=False)
    section = Column(String, nullable=False)
    crn = Column(Integer, nullable=False, primary_key=True)
    course_title = Column(String, nullable=False)
    meet_time = Column(ARRAY(String))
    instructor = Column(String, nullable=False)
    term = Column(Integer, nullable=False)
