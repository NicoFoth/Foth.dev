# Generated by Django 2.2.5 on 2021-03-05 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Suggestions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('date', models.DateTimeField(auto_now=True)),
                ('content', models.TextField()),
                ('upvotes', models.IntegerField(default=0)),
                ('downvotes', models.IntegerField(default=0)),
            ],
        ),
    ]