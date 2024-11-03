import datetime
import json
from typing import List, Dict


class Product:
    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price
        self.quantity = quantity

    def restock(self, amount: int):
        self.quantity += amount

    def purchase(self, amount: int) -> float:
        if amount > self.quantity:
            raise ValueError("Not enough stock available!")
        self.quantity -= amount
        return amount * self.price

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price}, quantity={self.quantity})"


class Inventory:
    def __init__(self):
        self.products: Dict[str, Product] = {}

    def add_product(self, product: Product):
        self.products[product.name] = product

    def get_product(self, name: str) -> Product:
        if name in self.products:
            return self.products[name]
        raise ValueError("Product not found in inventory!")

    def to_dict(self) -> Dict[str, dict]:
        return {name: product.__dict__ for name, product in self.products.items()}

    def save_inventory(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f)

    def load_inventory(self, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
            for name, info in data.items():
                product = Product(name, info['price'], info['quantity'])
                self.add_product(product)


def create_sample_inventory() -> Inventory:
    inventory = Inventory()
    inventory.add_product(Product("Apple", 0.5, 100))
    inventory.add_product(Product("Banana", 0.3, 150))
    inventory.add_product(Product("Orange", 0.8, 80))
    return inventory

def display_inventory(inventory: Inventory):
    print("Inventory:")
    for product in inventory.products.values():
        print(f"- {product.name}: ${product.price}, Quantity: {product.quantity}")


if __name__ == "__main__":
    inventory = create_sample_inventory()

    display_inventory(inventory)

    try:
        product_name = "Apple"
        quantity_to_buy = 10
        total_cost = inventory.get_product(product_name).purchase(quantity_to_buy)
        print(f"Purchased {quantity_to_buy} {product_name}(s) for ${total_cost:.2f}")
    except ValueError as e:
        print(e)

    product_name = "Banana"
    restock_amount = 20
    inventory.get_product(product_name).restock(restock_amount)
    print(f"Restocked {restock_amount} {product_name}(s).")

    display_inventory(inventory)

    inventory.save_inventory("inventory.json")
    print("Inventory saved to inventory.json")

    new_inventory = Inventory()
    new_inventory.load_inventory("inventory.json")
    print("Loaded inventory from inventory.json")
    display_inventory(new_inventory)
