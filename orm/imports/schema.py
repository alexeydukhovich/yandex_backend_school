from core.api import api
from core.database import db

from marshmallow import fields, validate, validates, ValidationError, post_dump
from marshmallow_sqlalchemy import ModelSchema, field_for

from orm.imports.model import Import
from orm.imports.citizens.schema import CitizenCreateSchema, CitizenGetSchema

@api.definition("ImportCreateSchema")
class ImportCreateSchema(ModelSchema):
    class Meta:
        model = Import
        sqla_session = db.session
    
    def handle_error(self, error, data):
        abort(HTTPStatus.BAD_REQUEST)

    import_id = field_for(Import, "import_id", required=False)
    citizens = fields.Nested("CitizenCreateSchema", many=True, required=True)

@api.definition("ImportCreateReturnSchema")
class ImportCreateReturnSchema(ModelSchema):
    class Meta:
        model = Import
        sqla_session = db.session

    import_id = field_for(Import, "import_id", required=False)

    @post_dump
    def wrap(self, data):
        if "citizens" in data:
            data.pop("citizens")
        return {
            "data": data
        }

@api.definition("ImportGetSchema")
class ImportGetSchema(ModelSchema):
    class Meta:
        model = Import
        sqla_session = db.session

    import_id = field_for(Import, "import_id", required=False)
    citizens = fields.Nested("CitizenGetSchema", many=True, required=True)