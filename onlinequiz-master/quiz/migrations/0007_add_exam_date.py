from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0006_alter_course_id_alter_question_id_alter_result_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='exam_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ] 