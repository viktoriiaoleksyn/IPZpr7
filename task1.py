from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """
    Контракт: будь-який платіжний сервіс зобов'язаний реалізувати метод pay.
    """
    @abstractmethod
    def pay(self, account_identifier: str, amount: float) -> bool:
        pass


class InternalBankProcessor(PaymentProcessor):
    def pay(self, account_identifier: str, amount: float) -> bool:
        print(f"[InternalBank] Списання {amount:.2f} грн з рахунку {account_identifier}")
        print("[InternalBank] Транзакцію успішно проведено через локальний кліринг.")
        return True

class GlobalPaySDK:
    def charge_customer(self, user_email: str, cents_amount: int, currency: str) -> dict:
        print(f"[GlobalPay SDK] Авторизація платежу для email: {user_email}")
        print(f"[GlobalPay SDK] Списано: {cents_amount} копійок ({currency})")
        return {"status": "SUCCESS", "tx_id": "GP-9841249"}

class GlobalPayAdapter(PaymentProcessor):
    """
    Адаптер огортає GlobalPaySDK та адаптує його під інтерфейс PaymentProcessor.
    """
    def __init__(self, sdk: GlobalPaySDK):
        self.sdk = sdk

    def pay(self, account_identifier: str, amount: float) -> bool:
        
        cents = int(round(amount * 100))
        
        
        result = self.sdk.charge_customer(
            user_email=account_identifier,
            cents_amount=cents,
            currency="UAH"
        )
        return result.get("status") == "SUCCESS"

class CheckoutService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

    def checkout(self, customer_info: str, total_price: float) -> None:
        print(f"\n>>> [CHECKOUT] Початок оформлення замовлення на суму: {total_price:.2f} грн")
        
        
        is_paid = self.payment_processor.pay(customer_info, total_price)
        
        if is_paid:
            print(">>> [CHECKOUT] Оплата пройшла! Формуємо накладну для відправки.")
        else:
            print(">>> [CHECKOUT] Помилка оплати!")

class CryptoPayService:
    def send_crypto_invoice(self, wallet_address, uah_sum):
        print(f"[CryptoPay] Транзакція на адресу {wallet_address}, сума {uah_sum:.2f} грн")
        return "OK"


class CryptoPayAdapter(PaymentProcessor):
    def __init__(self, crypto_service):
        self.crypto_service = crypto_service

    def pay(self, account_identifier, amount):
        result = self.crypto_service.send_crypto_invoice(account_identifier, amount)
        return result == "OK"


if __name__ == "__main__":
    
    print("--- 1. ОПЛАТА ЧЕРЕЗ ВНУТРІШНІЙ БАНК ---")
    local_processor = InternalBankProcessor()
    cart1 = CheckoutService(local_processor)
    cart1.checkout("UA413007200000026001234567890", 3500.00)

    print("\n--- 2. ОПЛАТА ЧЕРЕЗ АДАПТЕР GLOBALPAY ---")
    external_sdk = GlobalPaySDK()
    adapted_gateway = GlobalPayAdapter(external_sdk)
    cart2 = CheckoutService(adapted_gateway)
    cart2.checkout("customer@gmail.com", 3500.00)
    print("\n--- 3. ОПЛАТА ЧЕРЕЗ АДАПТЕР CRYPTOPAY ---")
    crypto = CryptoPayService()
    checkout_crypto = CheckoutService(CryptoPayAdapter(crypto))
    checkout_crypto.checkout("crypto_wallet_123", 3500.00)