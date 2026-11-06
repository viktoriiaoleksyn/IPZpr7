from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        """Єдиний метод для розрахунку вартості за конкретним алгоритмом."""
        pass


class PickupStrategy(ShippingStrategy):
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        return 0.0


class CourierStrategy(ShippingStrategy):
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        base_fee = 70.0
        distance_fee = distance_km * 5.0
        weight_fee = weight_kg * 2.5
        return round(base_fee + distance_fee + weight_fee, 2)


class ExpressDeliveryStrategy(ShippingStrategy):
    def calculate(self, weight_kg: float, distance_km: float) -> float:
        base_fee = 150.0
        cost = base_fee + (distance_km * 10.0)
        if weight_kg > 5.0:
            cost *= 1.3
        return round(cost, 2)


class OrderShippingContext:
    """
    Контекст зберігає посилання на одну зі стратегій і працює з нею через інтерфейс.
    Він не знає деталей реалізації конкретного тарифу.
    """
    def __init__(self, strategy: ShippingStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: ShippingStrategy) -> None:
        """Дозволяє змінювати алгоритм на льоту під час виконання програми."""
        self._strategy = strategy

    def calculate_delivery_cost(self, weight_kg: float, distance_km: float) -> float:
        return self._strategy.calculate(weight_kg, distance_km)


class PostMachineStrategy(ShippingStrategy):
    def calculate(self, weight_kg, distance_km):
        if weight_kg > 10:
            raise ValueError("Посилка занадто важка для поштомата (максимум 10 кг)")
        return 50.0


if __name__ == "__main__":
    weight = 6.0
    distance = 15.0

    context = OrderShippingContext(CourierStrategy())
    cost = context.calculate_delivery_cost(weight, distance)
    print(f"1. Кур'єрська доставка: {cost:.2f} грн")

    context.set_strategy(ExpressDeliveryStrategy())
    cost_express = context.calculate_delivery_cost(weight, distance)
    print(f"2. Експрес доставка: {cost_express:.2f} грн")

    context.set_strategy(PickupStrategy())
    cost_pickup = context.calculate_delivery_cost(weight, distance)
    print(f"3. Самовивіз: {cost_pickup:.2f} грн")
    context.set_strategy(PostMachineStrategy())
    print(f"4. Поштомат, 10 кг: {context.calculate_delivery_cost(10, distance):.2f} грн")
    try:
        context.calculate_delivery_cost(10.1, distance)
    except ValueError as error:
        print(f"5. Поштомат, 10.1 кг: {error}")