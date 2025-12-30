from sqlalchemy import (
    Column, String, Integer, Boolean, ForeignKey, Enum, create_engine
)
from sqlalchemy.orm import relationship, declarative_base
import enum
import uuid

Base = declarative_base()


# -------- ENUMS --------
class InstituteType(enum.Enum):
    COLLEGE = "COLLEGE"
    SCHOOL = "SCHOOL"
    COACHING = "COACHING"
    POLYTECHNIC = "POLYTECHNIC"


class InstituteLevel(enum.Enum):
    SEMESTER = "SEMESTER"
    CLASS = "CLASS"
    BATCH = "BATCH"


# -------- MODELS --------
class Institute(Base):
    __tablename__ = "institutes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    state = Column(String)
    city = Column(String)
    pincode = Column(String)
    type = Column(Enum(InstituteType))
    level_type = Column(Enum(InstituteLevel))
    levels = Column(Integer)

    admins = relationship("Admin", back_populates="institute")
    students = relationship("Student", back_populates="institute")
    classes = relationship("Class", back_populates="institute")
    mentors = relationship("Mentor", back_populates="institute")


class Admin(Base):
    __tablename__ = "admins"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    institute_id = Column(String, ForeignKey("institutes.id"))
    institute = relationship("Institute", back_populates="admins")

    mentors = relationship("Mentor", back_populates="admin")


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)

    institute_id = Column(String, ForeignKey("institutes.id"))
    institute = relationship("Institute", back_populates="mentors")

    admin_id = Column(String, ForeignKey("admins.id"))
    admin = relationship("Admin", back_populates="mentors")

    classes = relationship("Class", back_populates="mentor")


class Class(Base):
    __tablename__ = "classes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    level = Column(Integer)

    institute_id = Column(String, ForeignKey("institutes.id"))
    institute = relationship("Institute", back_populates="classes")

    mentor_id = Column(String, ForeignKey("mentors.id"))
    mentor = relationship("Mentor", back_populates="classes")

    students = relationship("Student", back_populates="class_")
    subjects = relationship("Subject", back_populates="class_")


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    enroll_no = Column(String)
    name = Column(String, nullable=False)
    email = Column(String)
    current_level = Column(Integer)

    institute_id = Column(String, ForeignKey("institutes.id"))
    institute = relationship("Institute", back_populates="students")

    class_id = Column(String, ForeignKey("classes.id"))
    class_ = relationship("Class", back_populates="students")

    progress = relationship("StudentProgress", back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    code = Column(String, unique=True)
    credit = Column(Integer)

    class_id = Column(String, ForeignKey("classes.id"))
    class_ = relationship("Class", back_populates="subjects")

    progress = relationship("StudentProgress", back_populates="subject")


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"))
    subject_id = Column(String, ForeignKey("subjects.id"))
    level = Column(Integer)
    marks = Column(Integer)
    attendance = Column(Integer)
    payment = Column(Boolean)
    rf=Column(Integer)


    student = relationship("Student", back_populates="progress")
    subject = relationship("Subject", back_populates="progress")
