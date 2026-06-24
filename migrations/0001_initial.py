from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='VoiceChannel',
            fields=[
                ('id', fields.BigIntField(primary_key=True, unique=True, db_index=True)),
                ('owner_id', fields.BigIntField()),
            ],
            options={'table': 'voice_channels', 'app': 'models', 'pk_attr': 'id', 'table_description': 'A bot-created dynamic voice channel and its owner.'},
            bases=['Model'],
        ),
    ]
