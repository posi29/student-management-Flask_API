from ..utils import db

class EnrollmentModel(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    score = db.Column(db.Float)

    def __repr__(self):
        return f'<Enrollment {self.id}>'
