"""Drop the tables of apps the old site had and this one does not: blog, book reviews,
thoughts, suggestions and Steam profiles. Nothing reads them any more.
"""
from django.db import migrations

TABLES = [
    'blog_blogarticle',
    'book_reviews_bookreviewarticle',
    'thoughts_thoughtarticles',
    'suggestions_suggestions',
    'users_profile',
]


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL([f'DROP TABLE IF EXISTS "{table}"' for table in TABLES], migrations.RunSQL.noop),
    ]
