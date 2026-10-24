import pytest
import requests

from data.products import ProductData
from api.api_manager import ApiManager
from data.users import UserData
from config.credentials import MANAGER_INVITE_CODE, ADMIN_INVITE_CODE

@pytest.fixture
def api_manager():
    session = requests.Session()
    yield ApiManager(session)
    session.close()

@pytest.fixture
def registered_user(api_manager):
    user_data  = UserData.registration_data()
    response = api_manager.auth_api.register_user(user_data)
    return {**user_data, "id": response.json()["id"]}

@pytest.fixture(scope="function")
def authenticated_user(api_manager):
    user_data = UserData.registration_data()
    register_response = api_manager.auth_api.register_user(user_data)

    api_manager.auth_api.authenticate((user_data["email"], user_data["password"]))

    return {**user_data, "id": register_response.json()["id"]}

@pytest.fixture(scope="function")
def manager_session():
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def manager_api(manager_session):
    return ApiManager(manager_session)

@pytest.fixture(scope="function")
def manager(manager_api: ApiManager):
    user_data = UserData.registration_data(invite_code=MANAGER_INVITE_CODE)
    manager_api.auth_api.authenticate((user_data["email"], user_data["password"]))
    return manager_api

@pytest.fixture(scope="function")
def admin_session():
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def admin_api(admin_session):
    return ApiManager(admin_session)

@pytest.fixture(scope="function")
def admin(admin_api: ApiManager):
    user_data = UserData.registration_data(invite_code=ADMIN_INVITE_CODE)
    admin_api.auth_api.register_user(user_data)
    admin_api.auth_api.authenticate((user_data["email"], user_data["password"]))
    return admin_api

@pytest.fixture(scope="function")
def created_product(admin_api:ApiManager):
    categories_response = admin_api.session.get("https://product.azon.130-17-2-195.sslip.io/api/v1/categories")
    category_id = categories_response.json()[0]["id"]

    product_data = ProductData.create_data(category_id)
    response = admin_api.products_api.create_product(product_data)
    created = response.json()

    yield created

    admin_api.products_api.delete_product(created["id"], expected_status=204)

@pytest.fixture(scope="function")
def user_session():
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def user_api(user_session):
    return ApiManager(user_session)

@pytest.fixture(scope="function")
def regular_user(user_api: ApiManager):
    user_data = UserData.registration_data()
    user_api.auth_api.register_user(user_data)
    user_api.auth_api.authenticate((user_data["email"], user_data["password"]))
    return user_api