# from sqlalchemy.sql.expression import null, text
# from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base
from sqlalchemy import Column, Integer, String

# class Quarter(Base):
#     __tablename__ = "posts"

# Subject Code: str
# Course Number: int
# Instruction Type: str
# Instruction Method: str
# Section: str
# CRN: int (primary key)
# Course Title: str


class Course(Base):
    __tablename__ = "course"
    subject_code = Column(String, nullable=False, primary_key=True)
    course_number = Column(Integer, nullable=False, primary_key=True)
    course_title = Column(String, nullable=False)
    college_id = Column(Integer, ForeignKey("college.id"))


class College(Base):
    __tablename__ = "college"

    id = Column(type_=Integer, primary_key=True, nullable=False)
    name = Column(type_=String, nullable=False)


class Instructor(Base):
    __tablename__ = "instructor"

    id = Column(type_=Integer, primary_key=True, nullable=False)
    first_name = Column(type_=String, nullable=False)
    middle_name = Column(type_=String)
    last_name = Column(type_=String, nullable=False)


class Quarter(Base):
    crn = Column(String, nullable=False, primary_key=True)
    subject_code = Column(String, nullable=False)
    course_number = Column(Integer, nullable=False)
    instruction_type = Column(String, nullable=False)
    instruction_method = Column(String, nullable=False)
    section = Column(String, nullable=False)
    start_time = Column(type_=TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(type_=TIMESTAMP(timezone=True), nullable=False)
    instructor_id = Column(Integer)
    __table_args__ = (ForeignKeyConstraint([subject_code, course_number],
                                           [Course.subject_code, Course.course_number]),
                      ForeignKeyConstraint(instructor_id, Instructor.id),
                      {})
