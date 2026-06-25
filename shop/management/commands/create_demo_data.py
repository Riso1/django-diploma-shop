from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from orders.models import Basket, BasketItem, DeliverySettings, Order, OrderItem, Payment
from shop.models import Category, Product, ProductReview, ProductSpecification, Sale, Tag
from users.models import Profile


class Command(BaseCommand):
    help = "Создаёт демонстрационные данные для интернет-магазина"

    def handle(self, *args, **options):
        delivery_settings = DeliverySettings.load()
        buyer_group, _ = Group.objects.get_or_create(name="Покупатель")

        User = get_user_model()

        def create_user(username, email, full_name, phone):
            first_name, *last_name_parts = full_name.split(" ", 1)
            last_name = last_name_parts[0] if last_name_parts else ""

            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                },
            )
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            user.set_password("123456")
            user.save()

            user.groups.add(buyer_group)

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = full_name
            profile.phone = phone
            profile.save()

            return user

        buyer_1 = create_user(
            username="ivan",
            email="ivan@example.com",
            full_name="Иван Петров",
            phone="+79000000001",
        )
        buyer_2 = create_user(
            username="anna",
            email="anna@example.com",
            full_name="Анна Смирнова",
            phone="+79000000002",
        )

        electronics, _ = Category.all_objects.update_or_create(
            title="Электроника",
            defaults={
                "parent": None,
                "is_active": True,
                "sort_index": 1,
                "is_deleted": False,
                "deleted_at": None,
            },
        )
        smartphones, _ = Category.all_objects.update_or_create(
            title="Смартфоны",
            defaults={
                "parent": electronics,
                "is_active": True,
                "sort_index": 1,
                "is_deleted": False,
                "deleted_at": None,
            },
        )
        laptops, _ = Category.all_objects.update_or_create(
            title="Ноутбуки",
            defaults={
                "parent": electronics,
                "is_active": True,
                "sort_index": 2,
                "is_deleted": False,
                "deleted_at": None,
            },
        )
        accessories, _ = Category.all_objects.update_or_create(
            title="Аксессуары",
            defaults={
                "parent": electronics,
                "is_active": True,
                "sort_index": 3,
                "is_deleted": False,
                "deleted_at": None,
            },
        )
        tv, _ = Category.all_objects.update_or_create(
            title="Телевизоры",
            defaults={
                "parent": electronics,
                "is_active": True,
                "sort_index": 4,
                "is_deleted": False,
                "deleted_at": None,
            },
        )

        tag_names = [
            "Новинка",
            "Хит продаж",
            "Скидка",
            "Игровое",
            "Для дома",
            "Ограниченный тираж",
        ]
        tags = {}
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tag.categories.set([electronics, smartphones, laptops, accessories, tv])
            tags[name] = tag

        def create_product(
            title,
            category,
            price,
            count,
            sort_index,
            purchases_count,
            rating,
            limited_edition,
            free_delivery,
            product_tags,
            specs,
        ):
            product, _ = Product.all_objects.update_or_create(
                title=title,
                defaults={
                    "category": category,
                    "description": f"{title}: краткое описание товара для каталога.",
                    "full_description": (
                        f"{title}: подробное описание товара для детальной страницы. "
                        "Подходит для демонстрации каталога, корзины и оформления заказа."
                    ),
                    "price": Decimal(price),
                    "count": count,
                    "free_delivery": free_delivery,
                    "limited_edition": limited_edition,
                    "is_active": True,
                    "sort_index": sort_index,
                    "purchases_count": purchases_count,
                    "rating": Decimal(rating),
                    "is_deleted": False,
                    "deleted_at": None,
                },
            )
            product.tags.set([tags[name] for name in product_tags])

            for spec_name, spec_value in specs.items():
                ProductSpecification.objects.update_or_create(
                    product=product,
                    name=spec_name,
                    defaults={"value": spec_value},
                )

            return product

        products = [
            create_product(
                "Смартфон Nova X",
                smartphones,
                "34990.00",
                15,
                1,
                120,
                "4.80",
                False,
                True,
                ["Хит продаж", "Новинка"],
                {"Производитель": "NovaTech", "Память": "128 ГБ", "Цвет": "Чёрный"},
            ),
            create_product(
                "Смартфон PixelPro 12",
                smartphones,
                "52990.00",
                8,
                2,
                98,
                "4.70",
                True,
                True,
                ["Ограниченный тираж", "Хит продаж"],
                {"Производитель": "PixelPro", "Память": "256 ГБ", "Цвет": "Синий"},
            ),
            create_product(
                "Ноутбук SkillBook 14",
                laptops,
                "74990.00",
                6,
                3,
                75,
                "4.60",
                False,
                True,
                ["Новинка", "Для дома"],
                {"Производитель": "SkillBook", "ОЗУ": "16 ГБ", "SSD": "512 ГБ"},
            ),
            create_product(
                "Игровой ноутбук Dragon 15",
                laptops,
                "119990.00",
                4,
                4,
                64,
                "4.90",
                True,
                True,
                ["Игровое", "Ограниченный тираж"],
                {"Производитель": "Dragon", "ОЗУ": "32 ГБ", "SSD": "1 ТБ"},
            ),
            create_product(
                "Беспроводные наушники AirSound",
                accessories,
                "7990.00",
                25,
                5,
                150,
                "4.50",
                False,
                False,
                ["Хит продаж", "Скидка"],
                {"Производитель": "AirSound", "Тип": "Bluetooth", "Цвет": "Белый"},
            ),
            create_product(
                "Мышь GameClick Pro",
                accessories,
                "2990.00",
                40,
                6,
                180,
                "4.40",
                False,
                False,
                ["Игровое", "Хит продаж"],
                {"Производитель": "GameClick", "Тип": "Проводная", "Цвет": "Чёрный"},
            ),
            create_product(
                "Клавиатура OfficeType",
                accessories,
                "4590.00",
                30,
                7,
                90,
                "4.30",
                False,
                False,
                ["Для дома"],
                {"Производитель": "OfficeType", "Тип": "Мембранная", "Цвет": "Серый"},
            ),
            create_product(
                "Телевизор Vision 55",
                tv,
                "57990.00",
                7,
                8,
                70,
                "4.60",
                False,
                True,
                ["Для дома", "Скидка"],
                {"Производитель": "Vision", "Диагональ": "55", "Разрешение": "4K"},
            ),
            create_product(
                "Телевизор CinemaMax 65",
                tv,
                "89990.00",
                3,
                9,
                55,
                "4.80",
                True,
                True,
                ["Ограниченный тираж", "Для дома"],
                {"Производитель": "CinemaMax", "Диагональ": "65", "Разрешение": "4K"},
            ),
            create_product(
                "Внешний SSD FastDrive 1TB",
                accessories,
                "9990.00",
                18,
                10,
                110,
                "4.70",
                False,
                False,
                ["Новинка"],
                {"Производитель": "FastDrive", "Объём": "1 ТБ", "Интерфейс": "USB-C"},
            ),
        ]

        Sale.objects.update_or_create(
            product=products[4],
            date_from=date(2026, 6, 1),
            defaults={
                "sale_price": Decimal("6490.00"),
                "date_to": date(2026, 7, 15),
                "is_active": True,
            },
        )
        Sale.objects.update_or_create(
            product=products[7],
            date_from=date(2026, 6, 1),
            defaults={
                "sale_price": Decimal("52990.00"),
                "date_to": date(2026, 7, 15),
                "is_active": True,
            },
        )

        ProductReview.objects.update_or_create(
            product=products[0],
            author="Иван Петров",
            defaults={
                "user": buyer_1,
                "email": buyer_1.email,
                "text": "Хороший смартфон, быстро работает и удобно лежит в руке.",
                "rate": 5,
                "is_active": True,
            },
        )
        ProductReview.objects.update_or_create(
            product=products[2],
            author="Анна Смирнова",
            defaults={
                "user": buyer_2,
                "email": buyer_2.email,
                "text": "Ноутбук подошёл для работы и учёбы, экран приятный.",
                "rate": 4,
                "is_active": True,
            },
        )
        ProductReview.objects.update_or_create(
            product=products[5],
            author="Иван Петров",
            defaults={
                "user": buyer_1,
                "email": buyer_1.email,
                "text": "Мышь удобная, для игр и обычной работы хватает.",
                "rate": 5,
                "is_active": True,
            },
        )

        Basket.objects.filter(user=buyer_1).delete()
        basket = Basket.objects.create(user=buyer_1)
        BasketItem.objects.create(basket=basket, product=products[0], count=1)
        BasketItem.objects.create(basket=basket, product=products[5], count=2)

        Order.all_objects.filter(comment__startswith="Демо-заказ").hard_delete()

        def create_order(user, items, delivery_type, payment_type, status, payment_status, number, error=""):
            subtotal = sum(product.price * count for product, count in items)

            if delivery_type == Order.DELIVERY_EXPRESS:
                delivery_cost = delivery_settings.express_delivery_price
            elif subtotal < delivery_settings.free_delivery_threshold:
                delivery_cost = delivery_settings.standard_delivery_price
            else:
                delivery_cost = Decimal("0.00")

            profile = user.profile

            order = Order.objects.create(
                user=user,
                full_name=profile.full_name,
                email=user.email,
                phone=profile.phone or "",
                delivery_type=delivery_type,
                payment_type=payment_type,
                city="Омск",
                address="ул. Учебная, д. 1",
                comment="Демо-заказ для проверки интернет-магазина",
                total_cost=subtotal + delivery_cost,
                delivery_cost=delivery_cost,
                status=status,
                payment_error=error,
            )

            for product, count in items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_title=product.title,
                    price=product.price,
                    count=count,
                )

            Payment.objects.create(
                order=order,
                number=number,
                status=payment_status,
                error=error,
            )

        create_order(
            user=buyer_1,
            items=[(products[0], 1), (products[5], 1)],
            delivery_type=Order.DELIVERY_ORDINARY,
            payment_type=Order.PAYMENT_ONLINE,
            status=Order.STATUS_PAID,
            payment_status=Payment.STATUS_SUCCESS,
            number="24682468",
        )

        create_order(
            user=buyer_2,
            items=[(products[4], 1)],
            delivery_type=Order.DELIVERY_EXPRESS,
            payment_type=Order.PAYMENT_SOMEONE,
            status=Order.STATUS_PAYMENT_ERROR,
            payment_status=Payment.STATUS_ERROR,
            number="12345670",
            error="Платёжная система отклонила оплату.",
        )

        self.stdout.write(self.style.SUCCESS("Демонстрационные данные созданы."))
        