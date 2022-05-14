item_schema = {
    "id": {"type": "string", "required": True, "empty": False, "regex": "\\S*"},
    "name": {"type": "string", "empty": False},
    "quantity": {"type": "integer", "min": 0},
}

item_list_schema = {
    "items": {
        "type": "list",
        "required": True,
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": item_schema,
        },
    },
}

item_deletion_schema = {
    "id": {"type": "string", "required": True, "empty": False, "regex": "\\S*"},
    "comment": {"type": "string", "required": True},
}

item_deletion_list_schema = {
    "items": {
        "type": "list",
        "required": True,
        "empty": False,
        "schema": {
            "type": "dict",
            "schema": item_deletion_schema,
        },
    },
}
