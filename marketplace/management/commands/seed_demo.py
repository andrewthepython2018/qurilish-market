from django.core.management.base import BaseCommand
from marketplace.models import Category, Product, Seller


class Command(BaseCommand):
    help = "Create demo categories, sellers, and products for Qurilish Market."

    def handle(self, *args, **options):
        categories = [
            ("Цемент", "cement", "Цемент для фундамента, кладки и отделочных работ."),
            ("Кирпич", "brick", "Кирпич и блоки для строительства домов и коммерческих объектов."),
            ("Металл", "metal", "Арматура, трубы, профили и листовой металл."),
            ("Сухие смеси", "dry-mixes", "Штукатурки, клеи и смеси для ремонта."),
        ]
        category_map = {}
        for name, slug, description in categories:
            category, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "description": description})
            category_map[slug] = category
        sellers = [
            ("Tashkent Build Supply", "+998 90 111 22 33", "Ташкент", "Яшнабадский район"),
            ("Samarkand Cement Trade", "+998 91 444 55 66", "Самарканд", "ул. Рудаки, 18"),
            ("Fergana Metal Group", "+998 93 777 88 99", "Фергана", "Промзона, склад 4"),
        ]
        seller_map = {}
        for name, phone, city, address in sellers:
            seller, _ = Seller.objects.update_or_create(name=name, defaults={"phone": phone, "city": city, "address": address, "is_active": True})
            seller_map[name] = seller
        products = [
            ("Цемент М400 50 кг", "cement-m400-50kg", "cement", "Tashkent Build Supply", "Надежный цемент для фундамента и кладочных работ.", 62000, "мешок", 350, "Ташкент"),
            ("Цемент М500 50 кг", "cement-m500-50kg", "cement", "Samarkand Cement Trade", "Высокопрочный цемент для ответственных конструкций.", 71000, "мешок", 260, "Самарканд"),
            ("Кирпич красный рядовой", "red-brick-standard", "brick", "Tashkent Build Supply", "Полнотелый кирпич для стен и перегородок.", 1450, "шт", 24000, "Ташкент"),
            ("Газоблок 600x300x200", "gas-block-600-300-200", "brick", "Samarkand Cement Trade", "Легкий блок для быстрого строительства стен.", 18500, "шт", 4200, "Самарканд"),
            ("Арматура A500C 12 мм", "rebar-a500c-12mm", "metal", "Fergana Metal Group", "Арматура для монолитных работ и фундамента.", 8200, "м", 12000, "Фергана"),
            ("Профильная труба 40x40", "profile-pipe-40x40", "metal", "Fergana Metal Group", "Металлическая труба для каркасов и навесов.", 28500, "м", 1800, "Фергана"),
            ("Клей для плитки C1", "tile-adhesive-c1", "dry-mixes", "Tashkent Build Supply", "Сухая смесь для укладки керамической плитки.", 54000, "мешок", 500, "Ташкент"),
            ("Штукатурка гипсовая 30 кг", "gypsum-plaster-30kg", "dry-mixes", "Samarkand Cement Trade", "Гипсовая штукатурка для внутренних стен.", 49000, "мешок", 310, "Самарканд"),
        ]
        for name, slug, category_slug, seller_name, description, price, unit, stock, city in products:
            Product.objects.update_or_create(slug=slug, defaults={"name": name, "category": category_map[category_slug], "seller": seller_map[seller_name], "description": description, "price": price, "unit": unit, "stock": stock, "city": city, "is_active": True})
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
