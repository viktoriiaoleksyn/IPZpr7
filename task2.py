import json
from abc import ABC, abstractmethod
from datetime import datetime

class Order:
    def __init__(self, order_id: int, customer: str, discount_percent: float = 0.0):
        self.order_id = order_id
        self.customer = customer
        self.discount_percent = discount_percent
        self.items: list[dict] = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_item(self, name: str, price: float, quantity: int = 1) -> None:
        self.items.append({"name": name, "price": price, "qty": quantity})

    def get_subtotal(self) -> float:
        return sum(item["price"] * item["qty"] for item in self.items)

    def get_total(self) -> float:
        subtotal = self.get_subtotal()
        return round(subtotal * (1 - self.discount_percent / 100), 2)


class InvoiceExporter(ABC):
    """
    Інтерфейс. Каже: 'Будь-який експортер чека ЗОБОВ'ЯЗАНИЙ мати метод export(order)'
    """
    @abstractmethod
    def export(self, order: Order) -> str:
        pass


class TextInvoiceExporter(InvoiceExporter):
    def export(self, order: Order) -> str:
        lines = [
            "=" * 40,
            f"ФІСКАЛЬНИЙ ЧЕК #{order.order_id}",
            f"Клієнт: {order.customer}",
            f"Час: {order.created_at}",
            "-" * 40,
        ]
        for item in order.items:
            cost = item["price"] * item["qty"]
            lines.append(f"{item['name']} x{item['qty']} = {cost:.2f} грн")
        lines.append("-" * 40)
        lines.append(f"Сума: {order.get_subtotal():.2f} грн")
        if order.discount_percent > 0:
            lines.append(f"Знижка: {order.discount_percent}%")
        lines.append(f"ДО ОПЛАТИ: {order.get_total():.2f} грн")
        lines.append("=" * 40)
        return "\n".join(lines)


class JsonInvoiceExporter(InvoiceExporter):
    def export(self, order: Order) -> str:
        payload = {
            "document": "INVOICE",
            "invoice_number": order.order_id,
            "client": order.customer,
            "timestamp": order.created_at,
            "lines": order.items,
            "pricing": {
                "subtotal": order.get_subtotal(),
                "discount_rate": order.discount_percent,
                "final_amount": order.get_total()
            }
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)


class HtmlInvoiceExporter(InvoiceExporter):
    def export(self, order: Order) -> str:
        rows = "".join(
            f"<tr><td>{i['name']}</td><td>{i['qty']}</td><td>{i['price']*i['qty']:.2f} грн</td></tr>"
            for i in order.items
        )
        return f"""<div style='font-family: Arial; border: 1px solid #333; padding: 12px; width: 340px;'>
  <h3>Рахунок #{order.order_id}</h3>
  <p>Клієнт: {order.customer}</p>
  <table border='1' width='100%' style='border-collapse: collapse;'>
    <tr><th>Товар</th><th>К-сть</th><th>Сума</th></tr>
    {rows}
  </table>
  <p><b>Всього до сплати: {order.get_total():.2f} грн</b></p>
</div>"""

class InvoiceProcessingService(ABC):
    
    @abstractmethod
    def create_exporter(self) -> InvoiceExporter:
        
        pass

    def process_and_print(self, order: Order) -> None:
        print(f"\n>>> [LOG] Обробка замовлення #{order.order_id}...")
        
        exporter = self.create_exporter()
        
        
        result = exporter.export(order)
        print(result)

class FastPosTerminalService(InvoiceProcessingService):
    def create_exporter(self) -> InvoiceExporter:
        return TextInvoiceExporter()


class ApiIntegrationService(InvoiceProcessingService):
    def create_exporter(self) -> InvoiceExporter:
        return JsonInvoiceExporter()


class EmailNotificationService(InvoiceProcessingService):
    def create_exporter(self) -> InvoiceExporter:
        return HtmlInvoiceExporter()

class MarkdownInvoiceExporter(InvoiceExporter):
    def export(self, order):
        lines = [f"# Чек №{order.order_id}", f"Клієнт: {order.customer}",
                "| Товар | Кількість | Сума |", "| --- | --- | --- |"]
        for item in order.items:
            lines.append(f"| {item['name']} | {item['qty']} | {item['price'] * item['qty']:.2f} грн |")
        lines.append(f"Разом до оплати: {order.get_total():.2f} грн")
        return "\n".join(lines)


class CsvInvoiceExporter(InvoiceExporter):
    def export(self, order):
        import csv
        from io import StringIO
        output = StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["Товар", "Кількість", "Ціна", "Сума"])
        for item in order.items:
            writer.writerow([item["name"], item["qty"], item["price"], item["price"] * item["qty"]])
        writer.writerow(["Разом до оплати", "", "", order.get_total()])
        return output.getvalue()


class MarkdownExportService(InvoiceProcessingService):
    def create_exporter(self):
        return MarkdownInvoiceExporter()


class CsvExportService(InvoiceProcessingService):
    def create_exporter(self):
        return CsvInvoiceExporter()


if __name__ == "__main__":
    order = Order(order_id=505, customer="Міккі Маус", discount_percent=15.0)
    order.add_item("Холодильник", 22000.0, 1)
    order.add_item("Набір посуду", 450.0, 2)

    
    FastPosTerminalService().process_and_print(order)
    ApiIntegrationService().process_and_print(order)
    EmailNotificationService().process_and_print(order)
    print("\n--- ЧЕК MARKDOWN ---")
    MarkdownExportService().process_and_print(order)
    print("\n--- ЧЕК CSV ---")
    CsvExportService().process_and_print(order)
