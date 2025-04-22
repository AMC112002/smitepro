from django.test import TestCase
from django.urls import reverse
from .models import Item, ItemCategory


class ItemCategoryModelTest(TestCase):
    def test_create_and_str(self):
        category = ItemCategory.objects.create(name="Inicial")
        self.assertEqual(category.name, "Inicial")
        self.assertEqual(str(category), "Inicial")

    def test_unique_name(self):
        ItemCategory.objects.create(name="Inicial")
        with self.assertRaises(Exception):
            ItemCategory.objects.create(name="Inicial")


class ItemModelTest(TestCase):
    def setUp(self):
        self.cat_power = ItemCategory.objects.create(name="Poder Mágico")
        self.cat_starter = ItemCategory.objects.create(name="Inicial")

    def test_create_basic_item(self):
        item = Item.objects.create(
            name="Reloj de Cronos",
            description="Reduce enfriamiento",
            price=800,
            tier=1
        )
        item.categories.add(self.cat_power)
        item.save()

        self.assertEqual(item.total_price, 800)
        self.assertIn(self.cat_power, item.categories.all())
        self.assertEqual(str(item), "Reloj de Cronos")

    def test_item_upgrade_total_price(self):
        base = Item.objects.create(name="Tomo Mágico", price=500, tier=1)
        upgraded = Item.objects.create(
            name="Libro del Alma",
            price=1100,
            from_item=base,
            tier=2
        )
        upgraded.save()

        self.assertEqual(upgraded.total_price, 1600)

    def test_json_stats_storage(self):
        item = Item.objects.create(name="Anillo Arcano", price=900)
        item.stats = {"Poder Mágico": 60, "Velocidad de Ataque": 10}
        item.save()

        self.assertIn("Poder Mágico", item.stats)
        self.assertEqual(item.stats["Poder Mágico"], 60)


class ItemViewsTest(TestCase):
    def setUp(self):
        self.cat_consumible = ItemCategory.objects.create(name="Consumible")
        self.cat_reliquia = ItemCategory.objects.create(name="Reliquia")
        self.cat_pasivo = ItemCategory.objects.create(name="Objeto Pasivo")

        # Consumible
        self.hp_pot = Item.objects.create(name="Poción de Vida", price=50, tier=1)
        self.hp_pot.categories.add(self.cat_consumible)

        # Reliquia Tier 1
        self.relic_t1 = Item.objects.create(name="Purificación", price=200, tier=1)
        self.relic_t1.categories.add(self.cat_reliquia)

        # Pasivo Tier 3
        self.pasivo_t3 = Item.objects.create(name="Amuleto del Guardián", price=2500, tier=3)
        self.pasivo_t3.categories.add(self.cat_pasivo)

    def test_item_list_view_status_and_template(self):
        response = self.client.get(reverse('item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'objetos/item_list.html')

    def test_item_list_view_context(self):
        response = self.client.get(reverse('item_list'))
        self.assertIn('consumables', response.context)
        self.assertIn(self.hp_pot, response.context['consumables'])

        self.assertIn('relics_tier1', response.context)
        self.assertIn(self.relic_t1, response.context['relics_tier1'])

        self.assertIn('passives_tier3', response.context)
        self.assertIn(self.pasivo_t3, response.context['passives_tier3'])

    def test_item_detail_view_ok(self):
        response = self.client.get(reverse('item_detail', args=[self.hp_pot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'objetos/item_detail.html')
        self.assertEqual(response.context['item'], self.hp_pot)

    def test_item_detail_404(self):
        response = self.client.get(reverse('item_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class ItemIntegrationTest(TestCase):
    def setUp(self):
        self.cat_inicial = ItemCategory.objects.create(name="Inicial")
        self.cat_pasivo = ItemCategory.objects.create(name="Objeto Pasivo")

        self.base_item = Item.objects.create(
            name="Botas Pequeñas",
            price=500,
            tier=1
        )
        self.base_item.categories.add(self.cat_inicial)

        self.upgraded_item = Item.objects.create(
            name="Botas Celestiales",
            price=800,
            from_item=self.base_item,
            tier=2
        )
        self.upgraded_item.categories.add(self.cat_pasivo)
        self.upgraded_item.save()

    def test_item_upgrade_shows_correct_total_price(self):
        self.assertEqual(self.upgraded_item.total_price, 1300)

    def test_navigation_from_list_to_detail_and_data(self):
        list_response = self.client.get(reverse('item_list'))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "Botas Pequeñas")

        detail_url = reverse('item_detail', args=[self.base_item.id])
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Botas Pequeñas")
