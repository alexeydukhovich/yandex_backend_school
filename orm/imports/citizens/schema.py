from datetime import datetime
from http import HTTPStatus

from core.api import api
from core.database import db

from flask_rest_api import abort


from marshmallow import fields, validate, validates, ValidationError, pre_load, pre_dump, post_dump
from marshmallow_sqlalchemy import ModelSchema, field_for

from orm.imports.citizens.model import Citizen, Relative


@api.definition("RelativeSchema")
class RelativeSchema(ModelSchema):
    class Meta:
        model = Relative
        sqla_session = db.session
    
    left_id = field_for(Relative, "left_id", required=True)
    #left_import_id = db.Column(db.Integer, db.ForeignKey('citizen.import_id'), primary_key=True)
    right_id = field_for(Relative, "right_id", required=True)
    #right_import_id = db.Column(db.Integer, db.ForeignKey('citizen.import_id'), primary_key=True)

    #left_citizen = field_for(Relative, "left_citizen", required=True)
    #right_citizen = field_for(Relative, "right_citizen", required=True)



@api.definition("CitizenCreateSchema")
class CitizenCreateSchema(ModelSchema):
    class Meta:
        model = Citizen
        sqla_session = db.session
        datetimeformat = '%d.%m.%Y'

    citizen_id = field_for(Citizen, "citizen_id", allow_none=False, required=True, validate=validate.Range(min = 0))

    town = field_for(Citizen, "town", allow_none=False, required=True, validate=validate.Length(min = 1, max = 256))
    street = field_for(Citizen, "street", allow_none=False, required=True, validate=validate.Length(min = 1, max = 256))
    building = field_for(Citizen, "building", allow_none=False, required=True, validate=validate.Length(min = 1, max = 256))
    apartment = field_for(Citizen, "apartment", allow_none=False, required=True, validate=validate.Range(min = 0))
    name = field_for(Citizen, "name", allow_none=False, required=True, validate=validate.Length(min = 1, max = 256))
    birth_date = field_for(Citizen, "birth_date", allow_none=False, required=True)
    gender = field_for(Citizen, "gender", allow_none=False, required=True, validate=validate.OneOf(["male", "female"]))
    as_left_edges = fields.Nested("RelativeSchema", many=True, required=True)
    as_right_edges = fields.Nested("RelativeSchema", many=True, required=True)

    def handle_error(self, error, data):
        abort(HTTPStatus.BAD_REQUEST)

    @validates("birth_date")
    def validates_birth_date(self, value):
        if value > datetime.utcnow():
            raise ValidationError("birth_day не может быть больше текущей даты.")
            
    @pre_load(pass_many=True)
    def handle_relatives(self, collection, many):
        if many:
            ids = {}

            for data in collection:
                ids[data["citizen_id"]] = data["relatives"] if "relatives" in data else []

            for data in collection:
                if "relatives" in data:
                    as_left_edges = []
                    as_right_edges = []
                    for other_citizen_id in data["relatives"]:

                        if other_citizen_id not in ids:
                            abort(HTTPStatus.BAD_REQUEST)
                        
                        if data["citizen_id"] not in ids[other_citizen_id]:
                            abort(HTTPStatus.BAD_REQUEST)

                        if data["citizen_id"] < other_citizen_id:
                            as_left_edges.append({"left_id": data["citizen_id"], "right_id": other_citizen_id})
                        elif data["citizen_id"] > other_citizen_id:
                            as_right_edges.append({"left_id": other_citizen_id, "right_id": data["citizen_id"]})
                        else:
                            abort(HTTPStatus.BAD_REQUEST)
                        
                    data["as_left_edges"] = as_left_edges
                    data["as_right_edges"] = []
                    #data["as_right_edges"] = as_right_edges
                    data.pop("relatives")
                
            return collection
        else:
            data = collection
            if "relatives" in data:
                as_left_edges = []
                as_right_edges = []
                for other_citizen_id in data["relatives"]:
                    if data["citizen_id"] < other_citizen_id:
                        as_left_edges.append({"left_id": data["citizen_id"], "right_id": other_citizen_id})
                    elif data["citizen_id"] > other_citizen_id:
                        as_right_edges.append({"left_id": other_citizen_id, "right_id": data["citizen_id"]})
                    else:
                        abort(HTTPStatus.BAD_REQUEST)
                data["as_left_edges"] = as_left_edges
                data["as_right_edges"] = []
                #data["as_right_edges"] = as_right_edges
                data.pop("relatives")
            return data

@api.definition("CitizenGetSchema")
class CitizenGetSchema(ModelSchema):
    class Meta:
        model = Citizen
        sqla_session = db.session
        datetimeformat = '%d.%m.%Y'

    citizen_id = field_for(Citizen, "citizen_id", required=True)
    #import_id = field_for(Citizen, "import_id", required=False)

    town = field_for(Citizen, "town", required=True)
    street = field_for(Citizen, "street", required=True)
    building = field_for(Citizen, "building", required=True)
    apartment = field_for(Citizen, "apartment", required=True)
    name = field_for(Citizen, "name", required=True)
    birth_date = field_for(Citizen, "birth_date", required=True)
    gender = field_for(Citizen, "gender", required=True)
    as_left_edges = fields.Nested("RelativeSchema", many=True, required=True)
    as_right_edges = fields.Nested("RelativeSchema", many=True, required=True)

    @post_dump(pass_many=True)
    def handle_relatives(self, collection, many):
        if many:
            for data in collection:
                as_left_edges = data.pop("as_left_edges")
                as_right_edges = data.pop("as_right_edges")
                relatives = []
                for edge in as_left_edges:
                    relatives.append(edge["right_id"])#["right_citizen"]["citizen_id"])
                for edge in as_right_edges:
                    relatives.append(edge["left_id"])#["left_citizen"]["citizen_id"])
                data["relatives"] = relatives
            return {
                "data": collection
            }
        else:
            data = collection
            as_left_edges = data.pop("as_left_edges")
            as_right_edges = data.pop("as_right_edges")
            relatives = []
            for edge in as_left_edges:
                relatives.append(edge["right_id"])#["right_citizen"]["citizen_id"])
            for edge in as_right_edges:
                relatives.append(edge["left_id"])#["left_citizen"]["citizen_id"])
            data["relatives"] = relatives
            return {
                "data": data
            }

        


@api.definition("CitizenPatchSchema")
class CitizenPatchSchema(ModelSchema):
    class Meta:
        model = Citizen
        sqla_session = db.session
        datetimeformat = '%d.%m.%Y'

    citizen_id = field_for(Citizen, "citizen_id", required=True)
    import_id = field_for(Citizen, "import_id", required=True)

    town = field_for(Citizen, "town", allow_none=False, required=False, validate=validate.Length(min = 1, max = 256))
    street = field_for(Citizen, "street", allow_none=False, required=False, validate=validate.Length(min = 1, max = 256))
    building = field_for(Citizen, "building", allow_none=False, required=False, validate=validate.Length(min = 1, max = 256))
    apartment = field_for(Citizen, "apartment", allow_none=False, required=False, validate=validate.Range(min = 1))
    name = field_for(Citizen, "name", allow_none=False, required=False, validate=validate.Length(min = 1, max = 256))
    birth_date = field_for(Citizen, "birth_date", allow_none=False, required=False)
    gender = field_for(Citizen, "gender", allow_none=False, required=False, validate=validate.OneOf(["male", "female"]))
    as_left_edges = fields.Nested("RelativeSchema", many=True, required=False)
    as_right_edges = fields.Nested("RelativeSchema", many=True, required=False)

    def handle_error(self, error, data):
        abort(HTTPStatus.BAD_REQUEST)

    @pre_load
    def handle_relatives(self, data):
        if "relatives" in data:
            as_left_edges = []
            as_right_edges = []
            for other_citizen_id in data["relatives"]:
                if data["citizen_id"] < other_citizen_id:
                    as_left_edges.append({"left_id": data["citizen_id"], "right_id": other_citizen_id})
                elif data["citizen_id"] > other_citizen_id:
                    as_right_edges.append({"left_id": other_citizen_id, "right_id": data["citizen_id"]})
                else:
                    #TODO Ну тут еррор
                    pass
            data["as_left_edges"] = as_left_edges
            #data["as_right_edges"] = []
            data["as_right_edges"] = as_right_edges
            data.pop("relatives")
        return data

