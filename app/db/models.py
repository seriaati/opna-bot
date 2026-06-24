from tortoise import fields
from tortoise.models import Model


class VoiceChannel(Model):
    """A bot-created dynamic voice channel and its owner."""

    id = fields.BigIntField(primary_key=True, generated=False)
    owner_id = fields.BigIntField()

    class Meta:
        table = "voice_channels"
