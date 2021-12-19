from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY

from .database import Base


class Quarter(Base):
    __tablename__ = "quarters"
    crn = Column(Integer, nullable=False, primary_key=True)
    term = Column(Integer, nullable=False, primary_key=True)
    subject_code = Column(String, nullable=False)
    course_number = Column(String, nullable=False)
    instr_type = Column(String, nullable=False)
    instr_method = Column(String, nullable=False)
    section = Column(String, nullable=False)
    course_title = Column(String, nullable=False)
    meet_time = Column(ARRAY(String))
    instructor = Column(String, nullable=False)
    coll_code = Column(String, nullable=False)


class Class(Base):
    subject_code = Column(String, nullable=False, primary_key=True)
    course_number = Column(String, nullable=False, primary_key=True)
    credit = Column(ARRAY(Integer), nullable=False)
    course_desc = Column(String, nullable=False)
    prereq = Column(String)
