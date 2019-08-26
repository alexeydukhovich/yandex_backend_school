from collections import OrderedDict
from copy import deepcopy
from enum import Enum
from functools import wraps

import flask_rest_api
from flask_rest_api.utils import deepupdate




class Blueprint(flask_rest_api.Blueprint):
    """
    PATCH: operation tags should be appended, not replaced
    """
    def register_views_in_doc(self, app, spec):
        for endpoint, endpoint_auto_doc in self._auto_docs.items():
            doc = OrderedDict()
            for key, auto_doc in endpoint_auto_doc.items():
                # Deepcopy to avoid mutating the source
                # Allows calling this function twice
                endpoint_doc = deepcopy(auto_doc)
                # Format operations documentation in OpenAPI structure
                self._prepare_doc(endpoint_doc, spec.openapi_version)

                # Merge auto_doc and manual_doc into doc
                manual_doc = self._manual_docs[endpoint][key]
                # Tag all operations with Blueprint name
                if 'tags' not in manual_doc:
                    manual_doc['tags'] = []
                manual_doc['tags'].append(self.name)
                doc[key] = deepupdate(endpoint_doc, manual_doc)

            # Thanks to self.route, there can only be one rule per endpoint
            full_endpoint = '.'.join((self.name, endpoint))
            rule = next(app.url_map.iter_rules(full_endpoint))
            # if APISPEC_VERSION_MAJOR < 1:
            #     spec.add_path(rule=rule, operations=doc)
            # else:
            spec.path(rule=rule, operations=doc)


    """
    PATCH: enum codes should generate int values
    """
    def response(self, *args, code=200, **kwargs):
        if isinstance(code, Enum):
            code = code.value
        return super().response(*args, code=code, **kwargs)

