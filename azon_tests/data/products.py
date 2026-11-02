import uuid
from utils.data_generator import DataGenerator


class ProductData:

    @staticmethod
    def create_data(category_id) -> dict:
        return {
            "name": f"Test Product {DataGenerator.generate_full_name()}",
            "description": f"Description for {DataGenerator.generate_full_name()}",
            "sku": f"SKU-{uuid.uuid4().hex[:8]}",
            "category_id": category_id,
            "price": 1999,
            "stock": 2,
        }

    @staticmethod
    def update_data() -> dict:
        return {
            "name": f"Updated {DataGenerator.generate_full_name()}",
        }

    @staticmethod
    def price_data(new_price: int) -> dict:
        return {"price": new_price}
