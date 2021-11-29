# Generated by Django 3.2.7 on 2021-11-29 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_type', models.CharField(blank=True, max_length=10, null=True)),
                ('batch_id', models.CharField(blank=True, max_length=50, null=True)),
                ('batch_status', models.CharField(blank=True, default='Waiting', max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email_address', models.CharField(blank=True, max_length=50, null=True)),
                ('email_password', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MachineIds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_identifier', models.CharField(blank=True, max_length=10, null=True)),
                ('machine_type', models.CharField(blank=True, max_length=10, null=True)),
                ('batch_amount', models.CharField(blank=True, max_length=4, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('req_date_created', models.CharField(blank=True, max_length=50, null=True)),
                ('updated_at', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('middle_initial', models.CharField(blank=True, max_length=10, null=True)),
                ('patient_id', models.CharField(blank=True, max_length=50, null=True)),
                ('sex', models.CharField(blank=True, max_length=10, null=True)),
                ('dob', models.CharField(max_length=50)),
                ('phone_no', models.CharField(blank=True, max_length=50, null=True)),
                ('email_address', models.CharField(blank=True, max_length=50, null=True)),
                ('mrn_no', models.CharField(blank=True, max_length=50, null=True)),
                ('patient_clinical_history', models.CharField(blank=True, max_length=400, null=True)),
                ('billing_address', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_state', models.CharField(blank=True, max_length=50, null=True)),
                ('billing_zipcode', models.CharField(blank=True, max_length=50, null=True)),
                ('bill_to', models.CharField(blank=True, max_length=50, null=True)),
                ('insurance_company', models.CharField(blank=True, max_length=50, null=True)),
                ('ins_pol_sub_nam', models.CharField(blank=True, max_length=50, null=True)),
                ('pat_rel_to_ins_pol_sub', models.CharField(blank=True, max_length=50, null=True)),
                ('pat_rel_address', models.CharField(blank=True, max_length=50, null=True)),
                ('pat_rel_state', models.CharField(blank=True, max_length=50, null=True)),
                ('pat_rel_zip', models.CharField(blank=True, max_length=50, null=True)),
                ('subscriber_no', models.CharField(blank=True, max_length=50, null=True)),
                ('group_no', models.CharField(blank=True, max_length=50, null=True)),
                ('medicare_no', models.CharField(blank=True, max_length=50, null=True)),
                ('client_name', models.CharField(blank=True, max_length=50, null=True)),
                ('anpac_id', models.CharField(blank=True, max_length=50, null=True)),
                ('sender_id', models.CharField(blank=True, max_length=50, null=True)),
                ('or_physician', models.CharField(blank=True, max_length=50, null=True)),
                ('or_physician_no', models.CharField(blank=True, max_length=50, null=True)),
                ('or_physician_email', models.CharField(blank=True, max_length=50, null=True)),
                ('date_collected', models.CharField(blank=True, max_length=50, null=True)),
                ('time_collected', models.CharField(blank=True, max_length=50, null=True)),
                ('collected_by', models.CharField(blank=True, max_length=50, null=True)),
                ('req_status', models.CharField(blank=True, default='Pending', max_length=50, null=True)),
                ('psa_choice', models.BooleanField(default=False)),
                ('afp_choice', models.BooleanField(default=False)),
                ('ca125_choice', models.BooleanField(default=False)),
                ('ca19_9_choice', models.BooleanField(default=False)),
                ('cea_choice', models.BooleanField(default=False)),
                ('cda_assay', models.BooleanField(default=False)),
                ('edited_notes', models.CharField(blank=True, max_length=200, null=True)),
                ('info_sub_by', models.CharField(blank=True, max_length=50, null=True)),
                ('info_qc_by', models.CharField(blank=True, max_length=50, null=True)),
                ('psa_score', models.CharField(blank=True, max_length=50, null=True)),
                ('afp_score', models.CharField(blank=True, max_length=50, null=True)),
                ('ca125_score', models.CharField(blank=True, max_length=50, null=True)),
                ('ca19_9_score', models.CharField(blank=True, max_length=50, null=True)),
                ('cea_score', models.CharField(blank=True, max_length=50, null=True)),
                ('cda_score', models.CharField(blank=True, max_length=50, null=True)),
                ('storage_location', models.CharField(blank=True, max_length=50, null=True)),
                ('psa_status', models.CharField(blank=True, max_length=50, null=True)),
                ('afp_status', models.CharField(blank=True, max_length=50, null=True)),
                ('ca125_status', models.CharField(blank=True, max_length=50, null=True)),
                ('ca19_9_status', models.CharField(blank=True, max_length=50, null=True)),
                ('cea_status', models.CharField(blank=True, max_length=50, null=True)),
                ('cda_status', models.CharField(blank=True, max_length=50, null=True)),
                ('cobas_status', models.CharField(blank=True, max_length=50, null=True)),
                ('cobas_test_operator', models.CharField(blank=True, max_length=50, null=True)),
                ('cda_test_operator', models.CharField(blank=True, max_length=50, null=True)),
                ('cda_model_assigned', models.CharField(blank=True, max_length=50, null=True)),
                ('cobas_model_assigned', models.CharField(blank=True, max_length=50, null=True)),
                ('batch_id_cobas', models.CharField(blank=True, max_length=50, null=True)),
                ('batch_id_cda', models.CharField(blank=True, max_length=50, null=True)),
                ('vol_amount', models.CharField(blank=True, max_length=50, null=True)),
                ('sample_type', models.CharField(blank=True, max_length=50, null=True)),
                ('cobas_test_notes', models.CharField(blank=True, max_length=200, null=True)),
                ('cda_test_notes', models.CharField(blank=True, max_length=200, null=True)),
                ('cobas_internal_notes', models.CharField(blank=True, max_length=200, null=True)),
                ('cda_internal_notes', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
