from flask import Flask, make_response, request
from cerberus import Validator

from inventory_mongo_client import InventoryMongoClient
from schemas import item_list_schema, item_deletion_list_schema
from responses import error_response

app = Flask(__name__)

client = InventoryMongoClient()


@app.route("/")
def base():
    return "Welcome to Inventory Manager"


@app.route("/inventory/items", methods=["GET"])
def get_items():
    # validate request arguments
    arg_dict, error = validate_request_args(request.args)
    if error:
        return error
    return client.get_items(**arg_dict)


@app.route("/inventory/items", methods=["POST"])
def create_or_update_items():
    data = request.json
    validator = Validator(item_list_schema, require_all=False)
    # validate request body against inventory schema
    items, error = validate_inventory_schema(data, validator)
    if error:
        return error
    return client.create_or_update_items(items)


@app.route("/inventory/items", methods=["DELETE"])
def delete_items():
    # check if user wants to be able to recover deleted items
    recover = request.args.get("recover", "true").lower() != "false"
    data = request.json
    validator = Validator(item_deletion_list_schema, require_all=True)
    # validate request body against inventory schema
    items, error = validate_inventory_schema(data, validator)
    if error:
        return error
    return client.delete_items(items, recover)


@app.route("/inventory/deleted_items", methods=["GET"])
def get_deleted_items():
    # validate request arguments
    arg_dict, error = validate_request_args(request.args)
    if error:
        return error
    return client.get_deleted_items(**arg_dict)


@app.route("/inventory/deleted_items", methods=["DELETE"])
def undelete_items():
    item_ids = request.args.getlist("id")
    if not item_ids:
        return error_response("Must specify ids of items to undelete.")
    if len(item_ids) != len(set(item_ids)):
        return error_response("Cannot provide duplicate ids.")
    return client.undelete_items(item_ids)


# validates given data against specified schema and checks for no
# duplicate items. returns any validation errors or returns items
# if validation is successful
def validate_inventory_schema(data, validator):
    if not validator.validate(data):
        return None, (validator.errors, 400)

    items = data["items"]
    item_ids = [item["id"] for item in items]
    if len(item_ids) != len(set(item_ids)):
        return None, error_response("Cannot specify items with duplicate ids.")

    return items, None


# parses and validates request arguments. returns any validation errors or returns arguments
# as a dict if validation is successful
def validate_request_args(args):
    arg_dict = {}
    item_ids = args.getlist("id")
    # remove duplicate item ids
    arg_dict["item_ids"] = list(set(item_ids))

    for arg_name in ["skip", "limit"]:
        arg = args.get(arg_name, None)
        if arg:
            if not arg.isdigit():
                return None, error_response(
                    f"'{arg_name}' argument must be a non-negative integer."
                )
            arg_dict[arg_name] = int(arg)

    return arg_dict, None


if __name__ == "__main__":
    app.run(port=8080)
