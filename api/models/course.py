from ..utils import db

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    login_id = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(10))

    students = db.relationship('StudentModel', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'
