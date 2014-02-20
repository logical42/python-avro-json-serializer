import avro.io
import avro.schema
from unittest import TestCase

from avro_json_serializer import AvroJsonSerializer

class TestAvroJsonSerializer(TestCase):
    FIELD_ENUM = {
        "type": "enum",
        "symbols": [
            "ORANGE",
            "APPLE",
            "PINEAPPLE"
        ],
        "name": "fruit"
    }

    FIELD_INT = {
        "name": "fint",
        "type": "int"
    }

    FIELD_LONG = {
        "name": "flong",
        "type": "long"
    }

    FIELD_FLOAT = {
        "name": "ffloat",
        "type": "float"
    }

    FIELD_DOUBLE = {
        "name": "fdouble",
        "type": "double"
    }

    FIELD_STRING = {
        "name": "fstring",
        "type": "string"
    }

    FIELD_ARRAY_INT = {
        "type": {"type": "array", "items": "int"},
        "name": "intarr"
    }

    FIELD_MAP_INT = {
        "type": {"type": "map", "values": "int"},
        "name": "intmap"
    }

    FIELD_FIXED = {
        "type": {
            "name": "fixed_16",
            "size": 16,
            "type": "fixed"
        },
        "size": 16,
        "name": "ffixed"
    }

    FIELD_RECORD = {
        "type": {
            "name": "Rec",
            "fields": [{
                "name": "subfint",
                "type": "int"
            }],
            "type": "record"
        },
        "name": "frec"
    }

    FIELD_UNION_NULL_INT = {
        "name": "funion_null",
        "type": [
            "int",
            "null"
        ]
    }

    FIELD_UNION_RECORDS = {
        "name": "funion_rec",
        "type": [
            {
                "type": "record",
                "name": "rec1",
                "fields": [
                    {
                        "name": "field",
                        "type": "int"
                    }
                ]
            },
            {
                "type": "record",
                "name": "rec2",
                "fields": [
                    {
                        "name": "field",
                        "type": "string"
                    }
                ]
            }
        ]
    }

    ALL_FIELDS_SCHEMA = {
        "type": "record",
        "name": "all_field",
        "fields": [
            FIELD_INT,
            FIELD_LONG,
            FIELD_STRING,
            FIELD_FIXED,
            FIELD_RECORD,
            FIELD_UNION_NULL_INT,
            FIELD_FLOAT,
            FIELD_DOUBLE
        ],
        "namespace": "com.some.thing"
    }

    UNION_FIELDS_SCHEMA = {
        "type": "record",
        "name": "unions",
        "fields": [
            FIELD_UNION_NULL_INT
        ]
    }

    UNION_RECORDS_SCHEMA = {
        "type": "record",
        "name": "unions",
        "fields": [
            FIELD_UNION_RECORDS
        ]
    }

    VALID_DATA_ALL_FIELDS = {
        "fint": 1,
        "flong": 1L,
        "ffloat": 1.0,
        "fdouble": 2.0,
        "fstring": "hi there",
        "ffixed": "1234567890123456",
        "frec": {
            "subfint": 2
        },
        "funion_null": None
    }

    def test_all_supported_types(self):
        avro_schema = avro.schema.make_avsc_object(self.ALL_FIELDS_SCHEMA, {})
        avro_json = AvroJsonSerializer(avro_schema).to_json(self.VALID_DATA_ALL_FIELDS)
        self.assertEquals(avro_json, """{"fint":1,"flong":1,"fstring":"hi there","ffixed":"1234567890123456","frec":{"subfint":2},"funion_null":null,"ffloat":1.0,"fdouble":2.0}""")

    def test_fails_validation(self):
        avro_schema = avro.schema.make_avsc_object(self.ALL_FIELDS_SCHEMA, {})
        data = dict(self.VALID_DATA_ALL_FIELDS)
        data["ffloat"] = "hi"
        serializer = AvroJsonSerializer(avro_schema)
        self.assertRaises(avro.io.AvroTypeException, serializer.to_json, data)

    def test_union_serialization_null(self):
        avro_schema = avro.schema.make_avsc_object(self.UNION_FIELDS_SCHEMA, {})
        data = {
            "funion_null": None
        }
        avro_json = AvroJsonSerializer(avro_schema).to_json(data)
        self.assertEquals(avro_json, """{"funion_null":null}""")

    def test_union_serialization_not_null(self):
        avro_schema = avro.schema.make_avsc_object(self.UNION_FIELDS_SCHEMA, {})
        data = {
            "funion_null": 1
        }
        avro_json = AvroJsonSerializer(avro_schema).to_json(data)
        self.assertEquals(avro_json, """{"funion_null":{"int":1}}""")

    def test_union_serialization_invalid(self):
        avro_schema = avro.schema.make_avsc_object(self.UNION_FIELDS_SCHEMA, {})
        data = {
            "funion_null": "hi"
        }
        serializer = AvroJsonSerializer(avro_schema)
        self.assertRaises(avro.io.AvroTypeException, serializer.to_json, data)

    def test_records_union(self):
        avro_schema = avro.schema.make_avsc_object(self.UNION_RECORDS_SCHEMA, {})
        data = {
            "funion_rec": {
                "field": 1
            }
        }
        avro_json = AvroJsonSerializer(avro_schema).to_json(data)
        self.assertEquals(avro_json, """{"funion_rec":{"rec1":{"field":1}}}""")

        data_another_record = {
            "funion_rec": {
                "field": "hi"
            }
        }
        another_record_json = AvroJsonSerializer(avro_schema).to_json(data_another_record)
        self.assertEquals(another_record_json, """{"funion_rec":{"rec2":{"field":"hi"}}}""")

    def test_map(self):
        schema_dict = {
            "type": "record",
            "name": "rec",
            "fields": [
                self.FIELD_MAP_INT
            ]
        }
        data = {
            "intmap": {
                "one": 1,
                "two": 2
            }
        }
        avro_schema = avro.schema.make_avsc_object(schema_dict, {})
        avro_json = AvroJsonSerializer(avro_schema).to_json(data)
        self.assertEquals(avro_json, """{"intmap":{"two":2,"one":1}}""")

    def test_array(self):
        schema_dict = {
            "type": "record",
            "name": "rec",
            "fields": [
                self.FIELD_ARRAY_INT
            ]
        }
        data = {
            "intarr": [1, 2, 3]
        }
        avro_schema = avro.schema.make_avsc_object(schema_dict, {})
        avro_json = AvroJsonSerializer(avro_schema).to_json(data)
        self.assertEquals(avro_json, """{"intarr":[1,2,3]}""")