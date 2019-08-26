from core.database import db
from flask_rest_api import abort
from http import HTTPStatus
from datetime import datetime

#

class Relative(db.Model):

    __tablename__ = "relative"
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['left_id', 'import_id'],
            ['citizen.citizen_id', 'citizen.import_id'],
        ),
        db.ForeignKeyConstraint(
            ['right_id', 'import_id'],
            ['citizen.citizen_id', 'citizen.import_id'],
        ),
    )



    left_id = db.Column(db.Integer, primary_key=True)
    import_id = db.Column(db.Integer, primary_key=True)
    right_id = db.Column(db.Integer, primary_key=True)
    

    __mapper_args__ = {
        "polymorphic_identity": "relative"
    }

class Citizen(db.Model):

    __tablename__ = "citizen"

    # Keys
    citizen_id = db.Column(db.Integer, primary_key=True)
    import_id = db.Column(db.Integer, db.ForeignKey('import.import_id'), primary_key=True)

    # Demographics
    town = db.Column(db.String(256))
    street = db.Column(db.String(256))
    building = db.Column(db.String(256))
    apartment = db.Column(db.Integer)
    name = db.Column(db.String(256))
    birth_date = db.Column(db.DateTime)
    gender = db.Column(db.String(6))

    as_left_edges = db.relationship("Relative", cascade="save-update, merge, delete, delete-orphan", backref='left_citizen', primaryjoin=(Relative.left_id==citizen_id) & (Relative.import_id == import_id))
    as_right_edges = db.relationship("Relative", cascade="save-update, merge, delete, delete-orphan", backref='right_citizen', primaryjoin=(Relative.right_id==citizen_id) & (Relative.import_id == import_id))

    __mapper_args__ = {
        "polymorphic_identity": "citizen"
    }


# left_id = db.Column(db.Integer, db.ForeignKey('citizen.citizen_id', name="a"), primary_key=True)
# left_import_id = db.Column(db.Integer, db.ForeignKey('citizen.import_id', name="a"), primary_key=True)
# right_id = db.Column(db.Integer, db.ForeignKey('citizen.citizen_id', name="b"), primary_key=True)
# right_import_id = db.Column(db.Integer, db.ForeignKey('citizen.import_id', name="b"), primary_key=True)


#right_import_id = db.Column(db.Integer, primary_key=True)

    #left_citizen = db.relationship(Citizen,
    #                            primaryjoin=(left_id==Citizen.citizen_id) & (import_id == Citizen.import_id),
    #                            back_populates='as_left_edges')
    #right_citizen = db.relationship(Citizen,
    #                            primaryjoin=(right_id==Citizen.citizen_id) & (import_id == Citizen.import_id),
    #                            back_populates='as_right_edges')

    # def __init__(self, c1, c2):
    #     if (c1.citizen_id < c2.citizen_id):
    #         self.left_citizen = n1
    #         self.right_citizen = n2
    #     else:
    #         self.left_citizen = n2
    #         self.right_citizen = n1