# -*- encoding: utf-8 -*-
# ! python3

import re

from django_make_app.exceptions import SchemaError
from django_make_app.utils import is_callable

MODEL_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


class YamlSchemaKeywords(object):
    APPS = "apps"
    APP_NAME = "name"
    MODELS = "models"


class StructureKeyword(object):
    NAME = "name"
    TYPE = "type"
    FOLDER = "folder"
    FILE = "file"
    RENDERER = "renderer"
    ITEMS = "items"
    TARGET_FILENAME = "_target_filename"
    TEMPLATE_NAME = "template_name"


MAPPINGS = {
    # Relations
    "fk": (lambda field_name, verbose_name: "ForeignKey(\"__app__.{to}\", verbose_name=\"{verbose_name}\")".format(to=field_name.title(), verbose_name=verbose_name)),
    "o2o": (lambda field_name, verbose_name: "ForeignKey(\"{to}\", verbose_name=\"{verbose_name}\")".format(to=field_name, verbose_name=verbose_name)),
    "m2m": (lambda field_name, verbose_name: "ForeignKey(\"{to}\", verbose_name=\"{verbose_name}\")".format(to=field_name, verbose_name=verbose_name)),

    # Types
    "text": (lambda field_name, verbose_name, *args, **kwargs: "TextField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "char": (lambda field_name, verbose_name, *args, **kwargs: "CharField(max_length={max_length},verbose_name=\"{verbose_name}\")".format(max_length=255, verbose_name=verbose_name)),
    "boolean": (lambda field_name, verbose_name, *args, **kwargs: "BooleanField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "date": (lambda field_name, verbose_name, *args, **kwargs: "DateField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "datetime": (lambda field_name, verbose_name, *args, **kwargs: "DateTimeField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "decimal": (lambda field_name, verbose_name, *args, **kwargs: "DecimalField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "filepath": (lambda field_name, verbose_name, *args, **kwargs: "FilePathField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "float": (lambda field_name, verbose_name, *args, **kwargs: "FloatField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "integer": (lambda field_name, verbose_name, *args, **kwargs: "IntegerField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "ip": (lambda field_name, verbose_name, *args, **kwargs: "IPAddressField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "gip": (lambda field_name, verbose_name, *args, **kwargs: "GenericIPAddressField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "nboolean": (lambda field_name, verbose_name, *args, **kwargs: "NullBooleanField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "time": (lambda field_name, verbose_name, *args, **kwargs: "TimeField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "binary": (lambda field_name, verbose_name, *args, **kwargs: "BinaryField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
    "auto": (lambda field_name, verbose_name, *args, **kwargs: "AutoField(verbose_name=\"{verbose_name}\")".format(verbose_name=verbose_name)),
}


def normalize_single_field(field):
    """
    :type field: unicode
    :rtype: dict
    """
    try:
        field_name, field_type, field_verbose_name = field.split(":")
    except ValueError:
        field_name, field_type = field.split(":"); field_verbose_name = field_name

    if not field_type or field_type not in MAPPINGS:
        raise SchemaError("Type {} is invalid".format(field_type))

    field_class = MAPPINGS.get(field_type)

    return {
        "name": field_name,
        "verbose_name": field_verbose_name,
        "class": field_class(field_name, field_verbose_name) if is_callable(field_class) else field_class
    }


def normalize_fields(fields):
    """
    :type fields: list of unicode
    :rtype: dict
    """
    for field in fields:
        yield normalize_single_field(field)


def validate_model_name(model_name):
    if not re.search(MODEL_NAME_RE, model_name):
        raise SchemaError(
            "\"{}\" is not a valid name of Django model.".format(model_name))


def normalize_single_model(model):
    """
    In e.g.: {'User': ['name', 'email']}

    :type model: dict
    :rtype: dict
    """
    for model_name_spec, model_fields in list(model.items()):
        try:
            model_name, model_verbose_name = model_name_spec.split(":")
        except ValueError:
            model_name, model_verbose_name = model_name_spec, model_verbose_name

        validate_model_name(model_name)

        return {
            "name": model_name,
            "verbose_name": model_verbose_name,
            "fields": [f for f in normalize_fields(model_fields)]
        }


def normalize_single_plain_model(model):
    """
    :type model: unicode
    :rtype: dict
    """
    try:
        model_name, model_verbose_name = model.split(":")
    except ValueError:
        model_name, model_verbose_name = model, model
    validate_model_name(model_name)

    return {
        "name": model_name,
        "verbose_name": model_verbose_name,
        "fields": []
    }


def normalize_models(models_list):
    """
    :type models_list: list
    :rtype: list
    """
    for model in models_list:
        if not isinstance(model, dict):
            yield normalize_single_plain_model(model)
        else:
            yield normalize_single_model(model)


def normalize_schema(innn):
    """
    :type innn: dict
    :rtype: dict
    """
    app_name = innn.get(YamlSchemaKeywords.APP_NAME)
    normalized_models = [i for i in normalize_models(
        innn.get(YamlSchemaKeywords.MODELS))]

    for model in normalized_models:
        for field in model.get('fields'):
            field['class'] = field['class'].replace("__app__", app_name)

    return {
        YamlSchemaKeywords.APP_NAME: app_name,
        YamlSchemaKeywords.MODELS: normalized_models
    }
