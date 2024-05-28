# Generated by Django 3.2.24 on 2024-05-28 10:07

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
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('balance', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now=True, null=True)),
                ('currency', models.CharField(blank=True, max_length=10, null=True)),
                ('delinquent', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('invoice_prefix', models.CharField(blank=True, max_length=50, null=True)),
                ('livemode', models.BooleanField(default=False)),
                ('next_invoice_sequence', models.IntegerField(default=1)),
                ('tax_exempt', models.CharField(default='none', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StripeEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_event_id', models.CharField(max_length=255, unique=True)),
                ('event_type', models.CharField(blank=True, max_length=255, null=True)),
                ('processed_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_subscription_id', models.CharField(max_length=255, unique=True)),
                ('status', models.CharField(max_length=50)),
                ('current_period_start', models.DateTimeField()),
                ('current_period_end', models.DateTimeField()),
                ('billing_cycle_anchor', models.DateTimeField()),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('canceled_at', models.DateTimeField(blank=True, null=True)),
                ('collection_method', models.CharField(max_length=50)),
                ('created', models.DateTimeField()),
                ('currency', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('livemode', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='stripeService.customer')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentIntent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_payment_intent_id', models.CharField(max_length=255, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_capturable', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('amount_received', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('currency', models.CharField(blank=True, max_length=10, null=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('capture_method', models.CharField(blank=True, max_length=50, null=True)),
                ('confirmation_method', models.CharField(blank=True, max_length=50, null=True)),
                ('livemode', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment_intents', to='stripeService.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_invoice_id', models.CharField(max_length=255, unique=True)),
                ('amount_due', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('currency', models.CharField(max_length=3)),
                ('status', models.CharField(max_length=50)),
                ('created', models.DateTimeField()),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('invoice_pdf', models.URLField(blank=True, null=True)),
                ('customer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='stripeService.customer')),
            ],
        ),
    ]
