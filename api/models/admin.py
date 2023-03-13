from ..utils import db
from ..models.users import User

class Admin(User):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    designation = db.Column(db.String(255) , nullable=True  )
    rc_number = db.Column(db.Integer, nullable=False)
    school_mail =  db.Column( db.String(100) , nullable=False , unique=True )
    is_superadmin = db.Column( db.Boolean , default=False)

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
