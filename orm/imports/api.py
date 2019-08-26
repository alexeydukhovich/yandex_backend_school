##### IMPORTS #####
from http import HTTPStatus
import json
from datetime import datetime
from numpy import percentile

from flask_rest_api import abort
from flask.views import MethodView
from flask.wrappers import Response
from flask import request, jsonify

from core.patches import Blueprint
from core.api import api
from core.database import db

from orm.imports.model import Import
from orm.imports.schema import ImportCreateSchema, ImportCreateReturnSchema, ImportGetSchema
from orm.imports.citizens.model import Citizen
from orm.imports.citizens.schema import CitizenGetSchema, CitizenPatchSchema


bp_import = Blueprint("imports", __name__, url_prefix="/imports")

@bp_import.route("")
class ImportCollection(MethodView):

    @bp_import.response(ImportGetSchema(many=True))
    def get(self):
        return Import.query.all()

    @bp_import.arguments(ImportCreateSchema)
    @bp_import.response(ImportCreateReturnSchema, code=HTTPStatus.CREATED)
    def post(self, new_import):
        db.session.add(new_import)
        db.session.commit()
        return new_import


@bp_import.route("/<int:import_id>/citizens")
class ImportCitizensContainer(MethodView):

    @bp_import.response(CitizenGetSchema(many=True))
    def get(self, import_id):
        import_instance = Import.query.get(import_id)

        if not import_instance:
            abort(HTTPStatus.BAD_REQUEST)
        
        return import_instance.citizens

@bp_import.route("/<int:import_id>/citizens/<int:citizen_id>")
class ImportCitizensContainerItem(MethodView):

    @bp_import.response(CitizenGetSchema)
    def get(self, import_id, citizen_id):
        citizen = Citizen.query.get((citizen_id, import_id))

        if not citizen:
            abort(HTTPStatus.BAD_REQUEST)
        
        return citizen
    
    #@bp_import.arguments(CitizenPatchSchema)
    @bp_import.response(CitizenGetSchema)
    def patch(self, import_id, citizen_id):

        #TODO Проверять, существуют ли указанные relatives

        update_data = request.json
        update_data["import_id"] = import_id
        update_data["citizen_id"] = citizen_id

        if "relatives" in update_data:
            for id in update_data["relatives"]:
                item = Citizen.query.get((id, import_id))
                if not item:
                    abort(HTTPStatus.BAD_REQUEST)

        update_data = CitizenPatchSchema().load(update_data)

        citizen = Citizen.query.get((citizen_id, import_id))

        has_changes = False

        for field_name in ["name", "gender", "birth_date", "as_left_edges", "as_right_edges", "town", "street", "building", "apartment"]:
            if hasattr(update_data, field_name):
                has_changes = True
                setattr(citizen, field_name, getattr(update_data, field_name))
        
        if not has_changes:
            abort(HTTPStatus.BAD_REQUEST)

        db.session.commit()
        return citizen

@bp_import.route("/<int:import_id>/citizens/birthdays")
class ImportCitizensContainerBirthdays(MethodView):

    def get(self, import_id):
        import_instance = Import.query.get(import_id)

        if not import_instance:
            abort(HTTPStatus.BAD_REQUEST)
        
        data = {
            "1":[],
            "2":[],
            "3":[],
            "4":[],
            "5":[],
            "6":[],
            "7":[],
            "8":[],
            "9":[],
            "10":[],
            "11":[],
            "12":[]
        }


        for citizen in import_instance.citizens:
            birth_month = str(citizen.birth_date.month)
            presents = len(citizen.as_left_edges) + len(citizen.as_right_edges)
            data[birth_month].append({"citizen_id": citizen.citizen_id, "presents": presents})
        
        return jsonify({
            "data": data
        })

@bp_import.route("/<int:import_id>/towns/stat/percentile/age")
class ImportCitizensContainerAges(MethodView):

    def get(self, import_id):
        import_instance = Import.query.get(import_id)

        if not import_instance:
            abort(HTTPStatus.BAD_REQUEST)
        
        towns = {}

        for citizen in import_instance.citizens:
            if citizen.town in towns: 
                towns[citizen.town].append(citizen)
            else:
                towns[citizen.town] = [citizen]
        
        data = []
        now = datetime.utcnow()

        for town, citizens in towns.items():

            ages = []

            for citizen in citizens:
                yearsdelta = now.year - citizen.birth_date.year
                monthdelta = now.month - citizen.birth_date.month
                daysdelta = now.day - citizen.birth_date.day

                age = 0

                if now.month > citizen.birth_date.month:
                    age = yearsdelta
                elif now.month < citizen.birth_date.month:
                    age = yearsdelta - 1
                elif now.day >= citizen.birth_date.day:
                    age = yearsdelta
                else:
                    age = yearsdelta - 1
                
                ages.append(age)

            p50 = percentile(ages, 50) 
            p75 = percentile(ages, 75)
            p99 = percentile(ages, 99)

            data.append({
                "town": town,
                "p50": p50,
                "p75": p75,
                "p99": p99
            })
            
            ages = []
        
        return jsonify({
            "data": data
        })
    




api.register_blueprint(bp_import)
