# Generated by Django 3.2.24 on 2024-05-13 22:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentIntent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_payment_intent_id', models.CharField(max_length=255, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_received', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(max_length=3)),
                ('status', models.CharField(max_length=50)),
                ('created', models.DateTimeField()),
                ('description', models.TextField(blank=True, null=True)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_intents', to='stripeService.customer')),
            ],
        ),
        migrations.CreateModel(
            name='RecurringPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interval', models.CharField(max_length=50)),
                ('next_payment_due', models.DateTimeField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_payments', to='stripeService.customer')),
                ('payment_intent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_details', to='stripeService.paymentintent')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_payment_method_id', models.CharField(max_length=255, unique=True)),
                ('type', models.CharField(max_length=50)),
                ('last4', models.CharField(blank=True, max_length=4, null=True)),
                ('exp_month', models.IntegerField(blank=True, null=True)),
                ('exp_year', models.IntegerField(blank=True, null=True)),
                ('brand', models.CharField(blank=True, max_length=50, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='stripeService.customer')),
            ],
        ),
        migrations.AddField(
            model_name='paymentintent',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stripeService.paymentmethod'),
        ),
    ]
