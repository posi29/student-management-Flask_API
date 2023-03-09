from ..utils import db

class StudentModel(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    gpa = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    enrollments = db.relationship('EnrollmentModel', backref='student', lazy=True)

    def __repr__(self):
        return f'<Student {self.name}>'

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)