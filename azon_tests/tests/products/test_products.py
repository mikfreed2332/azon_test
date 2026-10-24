from decimal import Decimal
import uuid



from data.products import ProductData


class TestProducts:

    def test_get_products_returns_paginated_catalog(self, api_manager):
        response = api_manager.products_api.get_products()

        data = response.json()
        assert data["total"] > 0
        assert len(data["items"]) <= data["size"]

    def test_products_price_filter(self, api_manager):
        response = api_manager.products_api.get_products(
            params={"price_min": 5000, "size": 100}
        )

        products = response.json()["items"]
        assert products, "Ожидали хотя бы один товар дороже 5000"
        for product in products:
            assert Decimal(product["price"]) >= 5000


    def test_get_product_by_id(self, api_manager):
        products = api_manager.products_api.get_products().json()["items"]
        product_id = products[0]["id"]

        response = api_manager.products_api.get_product(product_id)

        assert response.json()["id"] == product_id

    def test_get_nonexistent_product(self, api_manager):
        response = api_manager.products_api.get_product(uuid.uuid4(), expected_status=404)

        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_create_product(self, admin):
        categories = admin.session.get("https://product.azon.130-17-2-195.sslip.io/api/v1/categories").json()
        category_id = categories[0]["id"]

        product_data = ProductData.create_data(category_id)

        response = admin.products_api.create_product(product_data)
        assert response.status_code == 201

        created_product = response.json()
        assert created_product["name"] == product_data["name"]
        assert created_product["sku"] == product_data["sku"]
        assert float(created_product["price"]) == float(product_data["price"])

        admin.products_api.delete_product(created_product["id"], expected_status=204)


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
        assert float(updated_product["price"]) == float(new_price)

    def test_delete_product(self, admin):
        categories = admin.session.get("https://product.azon.130-17-2-195.sslip.io/api/v1/categories").json()
        category_id = categories[0]["id"]
        product_data = ProductData.create_data(category_id)
        create_response = admin.products_api.create_product(product_data)
        product_id = create_response.json()["id"]

        response = admin.products_api.delete_product(product_id)
        assert response.status_code == 204

    def test_create_product_without_token(self, api_manager):

        categories = api_manager.session.get("https://product.azon.130-17-2-195.sslip.io/api/v1/categories").json()
        category_id = categories[0]["id"]

        product_data = ProductData.create_data(category_id)

        response = api_manager.products_api.create_product(
            product_data,
            expected_status=401
        )
        assert response.json()["error"]["code"] == "TOKEN_MISSING"

    def test_create_product_without_role(self, regular_user):
        categories = regular_user.session.get("https://product.azon.130-17-2-195.sslip.io/api/v1/categories").json()
        category_id = categories[0]["id"]
        product_data = ProductData.create_data(category_id)

        response = regular_user.products_api.create_product(
            product_data,
            expected_status=403
        )

        assert response.json()["error"]["code"] == "FORBIDDEN"

    def test_create_product_with_duplicate_sku(self, admin, created_product):

        categories = admin.session.get("https://product.azon.130-17-2-195.sslip.io/api/v1/categories").json()
        category_id = categories[0]["id"]

        duplicate_data = ProductData.create_data(category_id)
        duplicate_data["sku"] = created_product["sku"]

        response = admin.products_api.create_product(
            duplicate_data,
            expected_status=409
        )

        assert response.json()["error"]["code"] == "SKU_EXISTS"

    def test_create_product_with_empty_boby(self, admin):
        response = admin.products_api.create_product(
            {},
            expected_status=422
        )

        assert response.status_code == 422
        assert "detail" in response.json()