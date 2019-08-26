from core.database import db

from orm.imports.citizens.model import Citizen, Relative



class Import(db.Model):

    __tablename__ = "import"

    import_id = db.Column(db.Integer, primary_key=True)
    citizens = db.relationship("Citizen", cascade="save-update, merge, delete, delete-orphan")

    __mapper_args__ = {
        "polymorphic_identity": "import"
    }
