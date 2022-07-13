

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('worry_board', '0001_initial'),
        ('jin', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='worryboard',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='worry_board.worryboard'),
        ),
    ]
