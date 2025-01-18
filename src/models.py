from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class DatabaseRecord:
    @staticmethod
    def extend_str_to(str: str, count: int):
        """Extend the line to `count` characters."""
        return str.ljust(count) + '\n'

    @staticmethod
    def make_record(len: int, *args):
        """Make a string for inserting into a table."""
        result = ''
        for value in args:
            result += str(value) + ';'
        return DatabaseRecord.extend_str_to(result[:-1], len)


class CarStatus(StrEnum):
    available = 'available'
    reserve = 'reserve'
    sold = 'sold'
    delivery = 'delivery'


class Car(BaseModel):
    vin: str
    model: int
    price: Decimal
    date_start: datetime
    status: CarStatus

    def index(self) -> str:
        return self.vin

    def make_record(self, len: int) -> str:
        """Make a string from a car object for inserting into a table."""
        return DatabaseRecord.make_record(len, self.vin, self.model, self.price, self.date_start, self.status)

    @classmethod
    def make_object(cls, record: str):
        """Make a car object from a record from a table."""
        car = record.strip().split(';')
        return cls(
            vin=car[0],
            model=int(car[1]),
            price=Decimal(car[2]),
            date_start=datetime.strptime(car[3], '%Y-%m-%d %X'),
            status=CarStatus(car[4])
        )


class Model(BaseModel):
    id: int
    name: str
    brand: str

    def index(self) -> str:
        return str(self.id)

    def make_record(self, len: int) -> str:
        """Make a string from a model object for inserting into a table."""
        return DatabaseRecord.make_record(len, self.id, self.name, self.brand)

    @classmethod
    def make_object(cls, record: str):
        """Make a model object from a record from a table."""
        model = record.strip().split(';')
        return cls(
            id=int(model[0]),
            name=model[1],
            brand=model[2]
        )


class Sale(BaseModel):
    sales_number: str
    car_vin: str
    sales_date: datetime
    cost: Decimal

    def index(self) -> str:
        return self.car_vin

    def make_record(self, len: int) -> str:
        """Make a string from a sale object for inserting into a table."""
        return DatabaseRecord.make_record(len, self.sales_number, self.car_vin, self.sales_date, self.cost)

    @classmethod
    def make_object(cls, record: str):
        """Make a sale object from a table's record."""
        sale = record.strip().split(';')
        return Sale(
            sales_number=sale[0],
            car_vin=sale[1],
            sales_date=datetime.strptime(sale[2], '%Y-%m-%d %X'),
            cost=Decimal(sale[3])
        )


class CarFullInfo(BaseModel):
    vin: str
    car_model_name: str
    car_model_brand: str
    price: Decimal
    date_start: datetime
    status: CarStatus
    sales_date: datetime | None
    sales_cost: Decimal | None


class ModelSaleStats(BaseModel):
    car_model_name: str
    brand: str
    sales_number: int