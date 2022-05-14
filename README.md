# Inventory Manager
Submission for the Fall 2022 Shopify Developer Intern Challenge Question

- [Features](#features)
- [How to Run](#how-to-run)
- [Application Endpoints](#application-endpoints)
  * [`GET /inventory/items`](#-get--inventory-items-)
    + [Query Arguments](#query-arguments)
    + [Sample Requests](#sample-requests)
  * [`POST /inventory/items`](#-post--inventory-items-)
    + [Sample Requests](#sample-requests-1)
  * [`DELETE /inventory/items`](#-delete--inventory-items-)
    + [Query Arguments](#query-arguments-1)
    + [Sample Requests](#sample-requests-2)
  * [`GET /inventory/deleted_items`](#-get--inventory-deleted-items-)
    + [Sample Requests](#sample-requests-3)
  * [`DELETE /inventory/deleted_items`](#-delete--inventory-deleted-items-)
    + [Sample Requests](#sample-requests-4)
- [Configuration Parameters](#configuration-parameters)


## Features
- Ability to create, read, update, delete, and undelete multiple inventory items at once
- **Selected feature:** Ability to delete items with deletion comments as well as undelete them 
- Use of LRU caches to store recently used items and deleted items, allowing for quicker item retrieval without needing
to query the database

## How to Run
### Run on repl.it
1. Go to https://replit.com/@JohnKattukudiyi/shopify-technical-challenge-submission
2. Click on "Run"
3. The application is now running, you can make HTTP requests to
https://shopify-technical-challenge-submission.johnkattukudiyi.repl.co and receive responses in return. This can be done
using cURL, Postman, etc. See [Application Endpoints](#application-endpoints) for the list of application endpoints. 

The following links contain pre-made requests that can be run immediately. **Note:** If prompted, select
"Proxy" as the interceptor.
- https://hopp.sh/r/5powCXjFeOC2
- https://hopp.sh/r/15LaLewaurpf
- https://hopp.sh/r/EeTq59c2QGh0
- https://hopp.sh/r/aIGIGE7ki3Nm
- https://hopp.sh/r/3v92oWmpUNQa

### Run locally
1. Initialize virtual environment with required dependencies (only needed when running the first time):
`make init`
2. Run application: `make run`
3. Send HTTP requests to `http://localhost:8080` to communicate with application

## Application Endpoints

### `GET /inventory/items`
Returns information about items in the `items` collection in the database with the given item ids, which are specified using the `id` query argument.
If no `id`s are given, it will return the result of querying the database for all items using given `skip` and `limit`
values, which can be specified via query arguments. Note that `skip` and `limit` are only used if no `id` values are specified,
otherwise they are ignored.

#### Query Arguments
- `id`: An id corresponding to an item for which to retrieve information. This argument can be repeated multiple times,
and the application will return information about all of the ids given. If no `id` values are specified, the application will attempt to query for all items in the database.
- `skip`: If no `id` values are specified, this value is used to determine the number of items to skip when querying for
all items in the database. For example, if there are 8 items in the database and we have a `skip` value of 3, only the
last 5 items will be returned. The given value must be a non-negative integer. Its default value is 0.
- `limit` If no `id` values are specified, this value is used to determine the limit on the number of items to return
when querying for all items in the database. The given value must be a non-negative integer. Its default value is
`DEFAULT_GET_ITEMS_QUERY_LIMIT` in `config.py`.

#### Sample Requests

Sample Successful Request 1
```
curl -X GET 'http://localhost:8080/inventory/items' | json_pp
```

Sample Successful Response 1
```
{
    "items": [
        {
            "id": "1",
            "name": "Test1",
            "quantity": 1
        },
        {
            "id": "2",
            "name": "Test2",
            "quantity": 2
        },
        {
            "id": "3",
            "name": "Test3",
            "quantity": 3
        },
        {
            "id": "4",
            "name": "Test4",
            "quantity": 4
        }
    ]
}
```

Sample Successful Request 2
```
curl -X GET 'http://localhost:8080/inventory/items?id=2&id=4' | json_pp
```

Sample Successful Response 2
```
{
    "items": [
        {
            "id": "2",
            "name": "Test2",
            "quantity": 2
        },
        {
            "id": "4",
            "name": "Test4",
            "quantity": 4
        }
    ]
}
```

Sample Successful Request 3
```
curl -X GET 'http://localhost:8080/inventory/items?skip=1&limit=2' | json_pp
```

Sample Successful Response 3
```
{
    "items": [
        {
            "id": "2",
            "name": "Test2",
            "quantity": 2
        },
        {
            "id": "3",
            "name": "Test3",
            "quantity": 3
        }
    ]
}
```

Sample Error Request 1
```
curl -X GET 'http://localhost:8080/inventory/items?skip=test' | json_pp
```

Sample Error Response 1
```
{
    "message": "'skip' argument must be a non-negative integer.",
    "status": "ERROR (400)"
}
```


### `POST /inventory/items`
Creates items with the ids and values specified in request body if they don't exist, or updates items
with the given values if they do exist. Each item consists of three fields:
- `id`: The item's unique id. Must be a non-empty string with no whitespace.
- `name`: The name of the item. Must be a non-empty string.
- `quantity`: The quantity of the item in the inventory. Must be a non-negative integer.

When creating items, all three fields are required, but when updating items, you only need to specify
the fields you would like to be updated with their new values, the other values will remain the same. The request body
must consist of a single field `items` containing a non-empty list of items with the fields described above.

#### Sample Requests

Sample Successful Request 1
```
curl -X POST 'http://localhost:8080/inventory/items' \
-H 'Content-Type: application/json' \
-d '{
    "items": [
        {
            "id": "1",
            "name": "Test1",
            "quantity": 1
        },
        {
            "id": "2",
            "name": "Test2",
            "quantity": 2
        },
        {
            "id": "3",
            "name": "Test3",
            "quantity": 3
        },
        {
            "id": "4",
            "name": "Test4",
            "quantity": 4
        }
    ]
}' | json_pp
```

Sample Successful Response 1
```
{
    "message": "{'writeErrors': [], 'writeConcernErrors': [], 'nInserted': 0, 'nUpserted': 4, 'nMatched': 0, 'nModified': 0, 'nRemoved': 0, 'upserted': [{'index': 0, '_id': '1'}, {'index': 1, '_id': '2'}, {'index': 2, '_id': '3'}, {'index': 3, '_id': '4'}]}",
    "status": "SUCCESS (200)"
}
```

Sample Successful Request 2
```
curl -X POST 'http://localhost:8080/inventory/items' \
-H 'Content-Type: application/json' \
-d '{
    "items": [
        {
            "id": "2",
            "name": "Updated Test2"
        },
        {
            "id": "3",
            "quantity": 300
        },
        {
            "id": "5",
            "name": "Test5",
            "quantity": 5
        }
    ]
}' | json_pp
```

Sample Successful Response 2
```
{
    "message": "{'writeErrors': [], 'writeConcernErrors': [], 'nInserted': 0, 'nUpserted': 1, 'nMatched': 2, 'nModified': 2, 'nRemoved': 0, 'upserted': [{'index': 2, '_id': '5'}]}",
    "status": "SUCCESS (200)"
}
```

Sample Error Request 1
```
curl -X POST 'http://localhost:8080/inventory/items' \
-H 'Content-Type: application/json' \
-d '{
    "items": [
        {
            "id": "6",
            "name": "Test6"
        }
    ]
}' | json_pp
```

Sample Error Response 1
```
{
    "message": "Validation error occurred: batch op errors occurred, full error: {'writeErrors': [{'index': 0, 'code': 121, 'errInfo': {'failingDocumentId': '6', 'details': {'operatorName': '$jsonSchema', 'schemaRulesNotSatisfied': [{'operatorName': 'required', 'specifiedAs': {'required': ['id', 'name', 'quantity']}, 'missingProperties': ['quantity']}]}}, 'errmsg': 'Document failed validation', 'op': SON([('q', {'_id': '6'}), ('u', {'$set': {'id': '6', 'name': 'Test6'}}), ('multi', False), ('upsert', True)])}], 'writeConcernErrors': [], 'nInserted': 0, 'nUpserted': 0, 'nMatched': 0, 'nModified': 0, 'nRemoved': 0, 'upserted': []}",
    "status": "ERROR (400)"
}
```

### `DELETE /inventory/items`
Deletes the items with the given ids and stores them in the `deleted_item` collection
with the given deletion comments. Each deletion request has two required fields:
- `id`: The id of the item to be deleted. Must be a non-empty string with no whitespace.
- `comment`: A comment about the deletion. Must be a string, can be left empty.

The request body must consist of a single field `items` containing a non-empty list of deletion requests with the fields
described above. 

**NOTE:** If there is already an item in the `deleted_item` collection with the same id as an item being
deleted, its information will be **overwritten** by the newly deleted item.

#### Query Arguments
- `recover`: If this argument is set to "false", the deleted items will not be backed up in the `deleted_items` collection
in the database. The default value is "true".

#### Sample Requests

Sample Successful Request 1
```
curl -X DELETE 'http://localhost:8080/inventory/items' \
-H 'Content-Type: application/json' \
-d '{
    "items": [
        {
            "id": "1",
            "comment": "Deletion comment 1"
        },
        {
            "id": "2",
            "comment": "Deletion comment 2"
        },
        {
            "id": "3",
            "comment": "Deletion comment 3"
        }
    ]
}' | json_pp
```

Sample Successful Response 1
```
{
    "message": "{'writeErrors': [], 'writeConcernErrors': [], 'nInserted': 0, 'nUpserted': 0, 'nMatched': 0, 'nModified': 0, 'nRemoved': 3, 'upserted': []}",
    "status": "SUCCESS (200)"
}
```


### `GET /inventory/deleted_items`
Gets stored copies of deleted items with the specified ids along with their associated deletion comment.
The `id`, `skip`, and `limit` query arguments function exactly as in `GET /inventory/items`.

#### Sample Requests

Sample Successful Request 1
```
curl -X GET 'http://localhost:8080/inventory/deleted_items' | json_pp
```

Sample Successful Response 1
```
{
    "items": [
        {
            "deletion_comment": "Deletion comment 1",
            "id": "1",
            "item": {
                "id": "1",
                "name": "Test1",
                "quantity": 1
            }
        },
        {
            "deletion_comment": "Deletion comment 2",
            "id": "2",
            "item": {
                "id": "2",
                "name": "2",
                "quantity": 2
            }
        },
        {
            "deletion_comment": "Deletion comment 3",
            "id": "3",
            "item": {
                "id": "3",
                "name": "Test3",
                "quantity": 3
            }
        }
    ]
}
```


### `DELETE /inventory/deleted_items`
Undeletes the deleted items with the specified ids and writes them back into the main `items` collection. Ids of items to
be undeleted are specified via the `id` query argument similar to as in `GET /inventory/items`. 

**NOTE:** If there is already an item in the `items` collection with the same id as an item being undeleted, its
information will be **overwritten** by the newly undeleted item.

#### Sample Requests

Sample Successful Request 1
```
curl -X DELETE 'http://localhost:8080/inventory/deleted_items?id=1&id=2&id=3' | json_pp
```

Sample Successful Response 1
```
{
    "message": "{'writeErrors': [], 'writeConcernErrors': [], 'nInserted': 0, 'nUpserted': 0, 'nMatched': 0, 'nModified': 0, 'nRemoved': 3, 'upserted': []}",
    "status": "SUCCESS (200)"
}
```

Sample Error Request 1
```
curl -X DELETE 'http://localhost:8080/inventory/deleted_items' | json_pp
```

Sample Error Response 1
```
{
    "message": "Must specify ids of items to undelete.",
    "status": "ERROR (400)"
}
```


## Configuration Parameters
The following parameters are found in `config.py`:
- `DEFAULT_CACHE_SIZE`: The default size of the item/deleted item caches.
- `DEFAULT_GET_ITEMS_QUERY_LIMIT`: The default value of `limit` used for queries retrieving all items/deleted items.
- `MONGODB_URL`: The URL of the MongoDB database to use for reading/writing items.
