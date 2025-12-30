import random
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker

from db import (
    Base, Institute, Admin, Mentor, Class, Student, Subject, StudentProgress,
    InstituteType, InstituteLevel
)

fake = Faker()

# ---------- 1. Create DB ----------
engine = create_engine("sqlite:///university.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# ---------- 2. Create 10 Institutes ----------
institutes = []
for i in range(10):
    inst = Institute(
        name=fake.company(),
        state=fake.state(),
        city=fake.city(),
        pincode=fake.zipcode(),
        type=random.choice(list(InstituteType)),
        level_type=random.choice(list(InstituteLevel)),
        levels=random.choice([4, 6, 8])
    )
    institutes.append(inst)
session.add_all(institutes)
session.commit()

# ---------- 3. Create 10 Admins ----------
admins = []
for i in range(10):
    admin = Admin(
        email=fake.unique.email(),
        institute=random.choice(institutes)
    )
    admins.append(admin)
session.add_all(admins)
session.commit()

# ---------- 4. Create 10 Mentors ----------
mentors = []
for i in range(10):
    mentor = Mentor(
        email=fake.unique.email(),
        institute=random.choice(institutes),
        admin=random.choice(admins)
    )
    mentors.append(mentor)
session.add_all(mentors)
session.commit()

# ---------- 5. Create 10 Classes ----------
classes = []
for i in range(10):
    cls = Class(
        name=f"Class {i+1}",
        level=i+1,
        institute=random.choice(institutes),
        mentor=random.choice(mentors)
    )
    classes.append(cls)
session.add_all(classes)
session.commit()

# ---------- 6. Create 10 Subjects per class ----------
subjects = []
for cls in classes:
    for i in range(10):
        sub = Subject(
            name=fake.word().capitalize(),
            code=fake.unique.lexify(text="???") + str(random.randint(100, 999)),
            credit=random.choice([3,4,5]),
            class_=cls
        )
        subjects.append(sub)
session.add(sub)
session.commit()

# ---------- 7. Create 40 Students ----------
students = []
for i in range(40):
    cls = random.choice(classes)
    stud = Student(
        enroll_no=f"STU{i+1:03d}",
        name=fake.name(),
        email=fake.email(),
        current_level=cls.level,
        institute=cls.institute,
        class_=cls
    )
    students.append(stud)
session.add_all(students)
session.commit()

# ---------- 8. Create StudentProgress ----------
# ---------- 8. Create StudentProgress with RF ----------
progress_entries = []
for student in students:
    for subject in student.class_.subjects:
        marks = random.randint(50, 100)
        attendance = random.randint(70, 100)

        # Example probabilistic risk factor: lower marks or attendance → higher RF
        rf = (100 - marks) / 100 * 0.7 + (100 - attendance) / 100 * 0.3
        rf = round(min(max(rf, 0), 1), 2)  # clamp to 0-1 and round to 2 decimals

        progress = StudentProgress(
            student=student,
            subject=subject,
            level=student.current_level,
            marks=marks,
            attendance=attendance,
            payment=random.choice([True, True, True, False]),
            rf=rf
        )
        progress_entries.append(progress)
session.add_all(progress_entries)
session.commit()

print("Database populated: 10 institutes, 10 admins, 10 mentors, 10 classes, 10 subjects per class, 40 students, student progress filled.")
# ---------- Print Institutes ----------
print("\n--- Institutes ---")
for inst in session.query(Institute).all():
    print(f"{inst.id[:8]} | {inst.name} | {inst.city} | {inst.type.value} | Levels: {inst.levels}")

# ---------- Print Admins ----------
print("\n--- Admins ---")
for admin in session.query(Admin).all():
    print(f"{admin.id[:8]} | {admin.email} | Institute: {admin.institute.name}")

# ---------- Print Mentors ----------
print("\n--- Mentors ---")
for mentor in session.query(Mentor).all():
    print(f"{mentor.id[:8]} | {mentor.email} | Institute: {mentor.institute.name} | Admin: {mentor.admin.email}")

# ---------- Print Classes ----------
print("\n--- Classes ---")
for cls in session.query(Class).all():
    print(f"{cls.id[:8]} | {cls.name} | Level: {cls.level} | Institute: {cls.institute.name} | Mentor: {cls.mentor.email}")

# ---------- Print Students ----------
print("\n--- Students ---")
for stud in session.query(Student).all():
    print(f"{stud.id[:8]} | {stud.name} | Enroll: {stud.enroll_no} | Class: {stud.class_.name} | Institute: {stud.institute.name}")

# ---------- Print Subjects ----------
print("\n--- Subjects ---")
for subj in session.query(Subject).all():
    print(f"{subj.id[:8]} | {subj.name} | Code: {subj.code} | Class: {subj.class_.name}")

# ---------- Print Student Progress with RF ----------
print("\n--- Student Progress ---")
for prog in session.query(StudentProgress).all():
    print(f"{prog.id[:8]} | Student: {prog.student.name} | Subject: {prog.subject.name} | Marks: {prog.marks} | Attendance: {prog.attendance} | RF: {prog.rf}")