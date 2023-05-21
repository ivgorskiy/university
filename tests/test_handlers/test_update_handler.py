import json
from uuid import uuid4

import pytest


async def test_update_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Original",
        "surname": "User",
        "email": "original@sdf.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
    }
    user_data_updated = {
        "name": "Update",
        "surname": "User",
        "email": "update@iii.com",
    }

    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(user_data["user_id"])
    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] is user_data["is_active"]
    assert user_from_db["user_id"] == user_data["user_id"]


async def test_update_user_check_one_is_updated(
    client, create_user_in_database, get_user_from_database
):
    user_data_one = {
        "user_id": uuid4(),
        "name": "One",
        "surname": "User",
        "email": "one@sdf.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
    }
    user_data_two = {
        "user_id": uuid4(),
        "name": "Two",
        "surname": "User",
        "email": "two@sdf.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
    }
    user_data_three = {
        "user_id": uuid4(),
        "name": "Three",
        "surname": "User",
        "email": "three@sdf.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
    }
    user_data_updated = {
        "name": "Updated",
        "surname": "OneUser",
        "email": "updated@sdf.com",
    }
    for user_data in [user_data_one, user_data_two, user_data_three]:
        await create_user_in_database(**user_data)

    resp = client.patch(
        f"/user/?user_id={user_data_one['user_id']}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data["updated_user_id"] == str(user_data_one["user_id"])
    users_from_db = await get_user_from_database(user_data_one["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_updated["name"]
    assert user_from_db["surname"] == user_data_updated["surname"]
    assert user_from_db["email"] == user_data_updated["email"]
    assert user_from_db["is_active"] is user_data_one["is_active"]
    assert user_from_db["user_id"] == user_data_one["user_id"]

    # check other users that data has not been changed
    users_from_db = await get_user_from_database(user_data_two["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_two["name"]
    assert user_from_db["surname"] == user_data_two["surname"]
    assert user_from_db["email"] == user_data_two["email"]
    assert user_from_db["is_active"] is user_data_two["is_active"]
    assert user_from_db["user_id"] == user_data_two["user_id"]

    users_from_db = await get_user_from_database(user_data_three["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_three["name"]
    assert user_from_db["surname"] == user_data_three["surname"]
    assert user_from_db["email"] == user_data_three["email"]
    assert user_from_db["is_active"] is user_data_three["is_active"]
    assert user_from_db["user_id"] == user_data_three["user_id"]


@pytest.mark.parametrize(
    "user_data_updated, expected_status_code, expected_detail",
    [
        # Test case 1: No parameters provided
        (
            {},
            422,
            {
                "detail": "At least one parameter for user update info should be provided"
            },
        ),
        # Test case 2: Name contains numbers
        ({"name": "123"}, 422, {"detail": "Name should contains only letters."}),
        # Test case 3: Empty email
        (
            {"email": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ]
            },
        ),
        # Test case 4: Empty surname
        (
            {"surname": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "surname"],
                        "msg": "ensure this value has at least 1 characters",
                        "type": "value_error.any_str.min_length",
                        "ctx": {"limit_value": 1},
                    }
                ]
            },
        ),
        # Test case 5: Empty name
        (
            {"name": ""},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "name"],
                        "msg": "ensure this value has at least 1 characters",
                        "type": "value_error.any_str.min_length",
                        "ctx": {"limit_value": 1},
                    }
                ]
            },
        ),
        # Test case 6: Surname contains numbers
        ({"surname": "123"}, 422, {"detail": "Surname should contains only letters"}),
        # Test case 7: Email contains numbers
        (
            {"email": "123"},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ]
            },
        ),
    ],
)
async def test_update_user_validation_error(
    client,
    create_user_in_database,
    get_user_from_database,
    user_data_updated,
    expected_status_code,
    expected_detail,
):
    """Test the validation of user data when updating a user"""
    user_data = {
        "user_id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "asdf@sdf.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
    }
    await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/?user_id={user_data['user_id']}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == expected_status_code
    resp_data = resp.json()
    assert resp_data == expected_detail


async def test_update_user_id_validation_error(client):
    user_data_updated = {
        "name": "User",
        "surname": "ValidationId",
        "email": "id@sdf.com",
    }
    incorrect_user_id = 123

    resp = client.patch(
        f"/user/?user_id={incorrect_user_id}", data=json.dumps(user_data_updated)
    )
    assert resp.status_code == 422
    data_from_response = resp.json()
    assert data_from_response == resp.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


async def test_update_user_not_found_error(client):
    user_data_updated = {"name": "Ivan", "surname": "Ivanov", "email": "ivan@sdf.com"}
    user_id = uuid4()

    resp = client.patch(f"/user/?user_id={user_id}", data=json.dumps(user_data_updated))
    assert resp.status_code == 404
    resp_data = resp.json()
    assert resp_data == {"detail": f"User with id {user_id} not found."}


async def test_update_user_duplicate_email_error(client, create_user_in_database):
    user_data_one = {
        "user_id": uuid4(),
        "name": "One",
        "surname": "User",
        "email": "one@sdf.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
    }
    user_data_two = {
        "user_id": uuid4(),
        "name": "Two",
        "surname": "User",
        "email": "two@sdf.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
    }
    user_data_updated = {"email": user_data_two["email"]}

    for user_data in [user_data_one, user_data_two]:
        await create_user_in_database(**user_data)

    resp = client.patch(
        f"/user/?user_id={user_data_one['user_id']}", data=json.dumps(user_data_updated)
    )

    assert resp.status_code == 503
    assert (
        'duplicate key value violates unique constraint "users_email_key"'
        in resp.json()["detail"]
    )
