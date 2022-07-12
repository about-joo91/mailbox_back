# Generated by Django 4.0.6 on 2022-07-12 01:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Cate_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('content', models.TextField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jin.category')),
            ],
        ),
        migrations.CreateModel(
            name='Letter_Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.IntegerField()),
                ('content', models.TextField()),
                ('letter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jin.letter')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=20, unique=True, verbose_name='사용자 계정')),
                ('password', models.CharField(max_length=128, verbose_name='비밀번호')),
                ('nickname', models.CharField(max_length=20, unique=True, verbose_name='닉네임')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='생성날짜')),
                ('update_date', models.DateTimeField(auto_now=True, verbose_name='수정날짜')),
                ('report_cnt', models.IntegerField(verbose_name='신고횟수')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User_Letter_Target_User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jin.user')),
                ('target_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jin.letter')),
            ],
        ),
        migrations.CreateModel(
            name='Letter_Review_Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jin.letter_review')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jin.user')),
            ],
        ),
        migrations.AddField(
            model_name='letter_review',
            name='review_author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jin.user'),
        ),
        migrations.AddField(
            model_name='letter',
            name='letter_author',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='jin.user'),
        ),
    ]
