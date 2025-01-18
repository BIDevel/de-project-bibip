from datetime import datetime
from decimal import Decimal 

from sortedcontainers import SortedDict
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale, DatabaseRecord as db


class CarService:

    def __find_record_of_obj(self, ind: str | int, file_name: str, dict: SortedDict) -> tuple[str, int] | None:
        """Считывает запись/строку и возвращаем ее + номер строки"""
        line_number = dict[ind] if ind in dict else None

        if line_number is not None:
            with open(self.root_directory_path + "/" + file_name, "r") as f:
                f.seek(line_number * (self.__record_len + self.__nl_size))
                val = f.read(self.__record_len)
                return val, line_number
        return None
    
    def __add_to_index_file(self, elem: int | str, file_name: str, dict: SortedDict) -> None:
        """Добавляет в индекс"""
        with open(self.root_directory_path + "/" + file_name, "w") as f:
            dict[elem] = len(dict)
            arr = []
            for i in dict.items():
                record = db.make_record(self.__record_len, i[0], i[1])
                arr.append(record)
            f.writelines(arr)
    
    def __find_car_by_vin(self, vin: str) -> tuple[Car, int] | None:
        """Находит запись по VIN и создаем объект.\n
        Возвращаем: объект и его индекс"""
        obj_line = self.__find_record_of_obj(vin, 'cars.txt', self.__car_indexes)
        return (Car.make_object(obj_line[0]), obj_line[1]) if obj_line else None

    def __find_model_by_id(self, model_id: int) -> Model | None:
        """Находит модель авто и создаем объект и индекс"""
        obj_line = self.__find_record_of_obj(model_id, 'models.txt', self.__model_indexes)
        return Model.make_object(obj_line[0]) if obj_line else None

    def __find_sale_by_car_vin(self, car_vin: str) -> Sale | None:
        """Находит продажу по ВИН и создаем объект."""
        obj_line = self.__find_record_of_obj(car_vin, 'sales.txt', self.__sale_indexes)
        return Sale.make_object(obj_line[0]) if obj_line else None

    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        # Длина строки в файле
        self.__record_len = 500
        # Длина знака переноса
        self.__nl_size = 2
         
        # создаем таблицы
        open(self.root_directory_path + "/models.txt", "a").close()
        open(self.root_directory_path + "/models_index.txt", 'a').close()
        open(self.root_directory_path + "/cars.txt", "a").close()
        open(self.root_directory_path + "/cars_index.txt", 'a').close()
        open(self.root_directory_path + "/sales.txt", "a").close()
        open(self.root_directory_path + "/sales_index.txt", 'a').close()
        self.__model_indexes = SortedDict()
        self.__car_indexes = SortedDict()
        self.__sale_indexes = SortedDict()

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        """Добавляет модель авто в таблицу и создает индекс."""
        result_str = model.make_record(self.__record_len)
        with open(self.root_directory_path + '/models.txt', 'a') as f:
            f.write(result_str)

        self.__add_to_index_file(model.id, 'models_index.txt', self.__model_indexes)

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        """Добавляет авто в таблицу и создает индекс."""
        result_str = car.make_record(self.__record_len)
        with open(self.root_directory_path + '/cars.txt', 'a') as f:
            f.write(result_str)

        self.__add_to_index_file(car.vin, 'cars_index.txt', self.__car_indexes)

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        """Сохраняет запись о продаже в таблицу и создает индекс."""
        result_str = sale.make_record(self.__record_len)
        with open(self.root_directory_path + '/sales.txt', 'a') as f:
            f.write(result_str)

        self.__add_to_index_file(sale.car_vin, 'sales_index.txt', self.__sale_indexes)

        car_index = self.__find_car_by_vin(sale.car_vin)
        if car_index:
            car, line_number = car_index
            car.status = CarStatus('sold')
            with open(self.root_directory_path + '/cars.txt', 'r+') as f:
                f.seek(line_number * (self.__record_len + self.__nl_size))
                line_to_write = car.make_record(self.__record_len)
                f.write(line_to_write)
        return car

     # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        """Получает все доступные для продажи авто, т.е. имеющие статус available."""
        available_cars = []
        with open(self.root_directory_path + '/cars.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line:  
                    break
                if status in line:
                    car = Car.make_object(line)
                    available_cars.append(car)
        return available_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        """Получает детальную информацию о авто по VIN."""
        sales_date: datetime | None = None
        sales_cost: Decimal | None = None

        # Находим авто
        car_index = self.__find_car_by_vin(vin)
        if not car_index:  
            return None

        car, _ = car_index
        # находим имя модели и авто
        model = self.__find_model_by_id(car.model)
        if not model:   
            return None

        # Ищем продажи
        if car.status == CarStatus.sold:
            sale = self.__find_sale_by_car_vin(vin)
            if sale:
                sales_date = sale.sales_date
                sales_cost = sale.cost

        return CarFullInfo(
            vin=vin,
            car_model_name=model.name,
            car_model_brand=model.brand,
            price=car.price,
            date_start=car.date_start,
            status=car.status,
            sales_date=sales_date,
            sales_cost=sales_cost,
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car | None:
        """Обновить VIN."""
        # находим индекс авто
        car_index = self.__find_car_by_vin(vin)
        if car_index:
            car, line_number = car_index
        else:
            return None

        # перезаписываем индекс
        with open(self.root_directory_path + '/cars_index.txt', 'w') as f:
            self.__car_indexes.pop(car.vin)
            self.__car_indexes[new_vin] = line_number
            arr = []
            for i in self.__car_indexes.items():
                record = db.make_record(self.__record_len, i[0], i[1])
                arr.append(record)
            f.writelines(arr)

        with open(self.root_directory_path + '/cars.txt', 'r+') as f:
            f.seek(line_number * (self.__record_len + self.__nl_size))
            car.vin = new_vin
            line_to_write = car.make_record(self.__record_len)
            f.write(line_to_write)
        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        """Удаляем запись о продажах в sales.txt."""
        # получаем VIN
        vin = sales_number.split('#')[1]
        # удаляем индекс из словаря по ключу и возвращаем его номер
        index_num = self.__sale_indexes.pop(vin)

        # пересчитвываем и перезаписываем индекс 
        for (key, value) in self.__sale_indexes.items():
            if value > index_num:
                self.__sale_indexes[key] -= 1
        arr = []
        for i in self.__sale_indexes.items():
            record = db.make_record(self.__record_len, i[0], i[1])
            arr.append(record)
        with open(self.root_directory_path + '/sales_index.txt', 'w') as f:
            f.writelines(arr)

        # удаляем запись из sales.txt
        cur_line = index_num + 1
        with open(self.root_directory_path + '/sales.txt', 'r+') as f:
            while True:
                f.seek(cur_line * (self.__record_len + self.__nl_size))
                line = f.read(self.__record_len)
                if not line:
                    break
                f.seek((cur_line - 1) * (self.__record_len + self.__nl_size))
                f.write(line)
                cur_line += 1
            f.seek((cur_line - 1) * (self.__record_len + self.__nl_size))
            f.truncate()

        # находим авто по VIN и меняем статус
        car_index = self.__find_car_by_vin(vin)
        if car_index:
            car, line_number = car_index
            car.status = CarStatus('available')
            with open(self.root_directory_path + '/cars.txt', 'r+') as f:
                f.seek(line_number * (self.__record_len + self.__nl_size))
                line_to_write = car.make_record(self.__record_len)
                f.write(line_to_write)
        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        """Находит топ 3 модели авто по количеству продаж."""
        model_sales_dict: dict[int, int] = {}

        # получаем все проданные авто и добавляем в словарь кол-во продаж модели
        with open(self.root_directory_path + '/sales.txt', 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                # получаем VIN из строки продаж
                car_vin = line.strip().split(';')[1]

                # находим авто
                car = self.__find_car_by_vin(car_vin)
                if car:
                    car_model = car[0].model
                    # добавляем в словарь а если уже есть то инкремент
                    model_sales_dict[car_model] = model_sales_dict[car_model] + \
                        1 if car_model in model_sales_dict else 1

        # сортируем по кол-ву и берем первые три элемента
        top_3_models = sorted(model_sales_dict.items(),
                              key=lambda x: x[1], reverse=True)[:3]

        model_sale_stats: list[ModelSaleStats] = []

        # получаем имя бренда и модели
        for model_id, count in top_3_models:
            model = self.__find_model_by_id(model_id)
            if model:
                model_sale_stats.append(
                        ModelSaleStats(
                            car_model_name=model.name,
                            brand=model.brand,
                            sales_number=count
                        )
                    )

        return model_sale_stats