from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#fff0f5', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#ffb6c1', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#cd5c5c', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
