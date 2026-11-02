from decimal import Decimal
import uuid

from data.products import ProductData


class TestProducts:

    def test_get_products_returns_paginated_catalog(self, api_manager):
        response = api_manager.products_api.get_products()

        data = response.json()
        assert data["total"] > 0
        assert len(data["items"]) <= data["size"]

    def test_products_search_name(self, admin, created_product):
        search_name = created_product["name"]
        response = admin.products_api.get_products(params={"search": search_name})

        assert response.status_code == 200
        products = response.json()["items"]
        assert len(products) >= 1

        product_ids = [p["id"] for p in products]
        assert created_product["id"] in product_ids

        for product in products:
            assert search_name in product["name"]

    def test_get_product_by_id(self, api_manager):
        products = api_manager.products_api.get_products().json()["items"]
        product_id = products[0]["id"]

        response = api_manager.products_api.get_product(product_id)

        assert response.json()["id"] == product_id

    def test_get_nonexistent_product(self, api_manager):
        response = api_manager.products_api.get_product(uuid.uuid4(), expected_status=404)

        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_create_product(self, admin, category_id):
        product_data = ProductData.create_data(category_id)
        response = admin.products_api.create_product(product_data)
        assert response.status_code == 201

        created_product = response.json()
        assert created_product["name"] == product_data["name"]
        assert created_product["sku"] == product_data["sku"]
        assert Decimal(created_product["price"]) == Decimal(product_data["price"])

    def test_update_product(self, admin, created_product):
        update_data = ProductData.update_data()
        response = admin.products_api.update_product(created_product["id"], update_data)

        assert response.status_code == 200

        updated_product = response.json()
        assert updated_product["name"] == update_data["name"]

    def test_update_price(self, admin, created_product):
        new_price = 2499
        price_data = ProductData.price_data(new_price)
        response = admin.products_api.update_price(created_product["id"], price_data)

        assert response.status_code == 200

        updated_product = response.json()
        assert Decimal(updated_product["price"]) == Decimal(new_price)

    def test_delete_product(self, admin, api_manager, category_id):
        product_data = ProductData.create_data(category_id)
        create_response = admin.products_api.create_product(product_data)
        product_id = create_response.json()["id"]

        response = admin.products_api.delete_product(product_id)
        assert response.status_code == 204

        get_response = api_manager.products_api.get_product(product_id, expected_status=404)
        assert get_response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_create_product_without_token(self, api_manager, category_id):
        product_data = ProductData.create_data(category_id)
        response = api_manager.products_api.create_product(product_data, expected_status=401)
        assert response.json()["error"]["code"] == "TOKEN_MISSING"

    def test_create_product_without_role(self, regular_user, category_id):
        product_data = ProductData.create_data(category_id)
        response = regular_user.products_api.create_product(product_data, expected_status=403)

        assert response.json()["error"]["code"] == "FORBIDDEN"

    def test_create_product_with_duplicate_sku(self, admin, created_product, category_id):
        duplicate_data = ProductData.create_data(category_id)
        duplicate_data["sku"] = created_product["sku"]
        response = admin.products_api.create_product(duplicate_data, expected_status=409)

        assert response.json()["error"]["code"] == "SKU_EXISTS"

    def test_create_product_with_empty_body(self, admin):
        response = admin.products_api.create_product({}, expected_status=422)
        required_fields = ["category_id", "description", "name", "price", "sku", "stock"]
        error_details = response.json()["detail"]
        error_fields = [detail["loc"][-1] for detail in error_details]

        assert response.status_code == 422
        for filed in required_fields:
            assert filed in error_fields
