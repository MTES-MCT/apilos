# Generated by Django 4.2.11 on 2024-04-19 09:39

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("users", "0001_initial"),
        ("users", "0002_role"),
        ("users", "0003_user_cerbere_uid"),
        ("users", "0004_remove_user_cerbere_uid"),
        ("users", "0005_user_administrateur_de_compte"),
        ("users", "0006_user_telephone"),
        ("users", "0007_user_preferences_email"),
        ("users", "0008_user_filtre_departements"),
        ("users", "0009_alter_user_filtre_departements"),
        ("users", "0010_user_cerbere_login"),
        ("users", "0010_auto_20220531_1051"),
        ("users", "0011_merge_0010_auto_20220531_1051_0010_user_cerbere_login"),
        ("users", "0012_alter_role_typologie"),
        ("users", "0013_auto_20220906_1022"),
        ("users", "0014_remove_useless_permissions"),
        ("users", "0015_user_creator"),
        ("users", "0016_alter_user_preferences_email"),
        ("users", "0017_alter_role_administration_alter_role_bailleur_and_more"),
        ("users", "0018_historicaluser"),
        ("users", "0019_historicalrole"),
        ("users", "0020_remove_historicaluser_last_login"),
        ("users", "0021_historicaluser_read_popup_user_read_popup"),
        ("users", "0022_alter_historicalrole_typologie_alter_role_typologie"),
        ("users", "0023_alter_role_unique_together"),
        ("users", "0024_remove_read_popup"),
    ]

    dependencies = [
        ("bailleurs", "0001_initial_squashed_0027_remove_search_vector_trigger"),
        ("apilos_settings", "0001_initial_squashed_0004_auto_20230207_2328"),
        ("instructeurs", "0001_initial_squashed_0017_auto_20230925_1209"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
                ("administrateur_de_compte", models.BooleanField(default=False)),
                ("telephone", models.CharField(max_length=25, null=True)),
                (
                    "preferences_email",
                    models.CharField(
                        choices=[
                            ("TOUS", "Tous les emails"),
                            ("PARTIEL", "Emails des conventions instruites"),
                            ("AUCUN", "Aucun email"),
                        ],
                        default="PARTIEL",
                        max_length=25,
                    ),
                ),
                (
                    "filtre_departements",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Les programmes et conventions affichés à l'utilisateur seront filtrés en utilisant la liste des départements ci-dessous",
                        related_name="filtre_departements",
                        to="apilos_settings.departement",
                    ),
                ),
                ("cerbere_login", models.CharField(max_length=255, null=True)),
                (
                    "creator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="HistoricalUser",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        db_index=True,
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("administrateur_de_compte", models.BooleanField(default=False)),
                ("telephone", models.CharField(max_length=25, null=True)),
                ("cerbere_login", models.CharField(max_length=255, null=True)),
                (
                    "preferences_email",
                    models.CharField(
                        choices=[
                            ("TOUS", "Tous les emails"),
                            ("PARTIEL", "Emails des conventions instruites"),
                            ("AUCUN", "Aucun email"),
                        ],
                        default="PARTIEL",
                        max_length=25,
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical user",
                "verbose_name_plural": "historical users",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="HistoricalRole",
            fields=[
                ("id", models.IntegerField(blank=True, db_index=True)),
                (
                    "typologie",
                    models.CharField(
                        choices=[
                            ("INSTRUCTEUR", "Instructeur"),
                            ("BAILLEUR", "Bailleur"),
                            ("ADMINISTRATEUR", "Administrateur"),
                        ],
                        default="BAILLEUR",
                        max_length=25,
                    ),
                ),
                ("perimetre_region", models.CharField(max_length=10, null=True)),
                ("perimetre_departement", models.CharField(max_length=10, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "administration",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="instructeurs.administration",
                    ),
                ),
                (
                    "bailleur",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="bailleurs.bailleur",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="auth.group",
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical role",
                "verbose_name_plural": "historical roles",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "typologie",
                    models.CharField(
                        choices=[
                            ("INSTRUCTEUR", "Instructeur"),
                            ("BAILLEUR", "Bailleur"),
                            ("ADMINISTRATEUR", "Administrateur"),
                        ],
                        default="BAILLEUR",
                        max_length=25,
                    ),
                ),
                (
                    "administration",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="instructeurs.administration",
                    ),
                ),
                (
                    "bailleur",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="bailleurs.bailleur",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="auth.group",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("perimetre_departement", models.CharField(max_length=10, null=True)),
                ("perimetre_region", models.CharField(max_length=10, null=True)),
            ],
            options={
                "unique_together": {
                    ("typologie", "bailleur", "administration", "user")
                },
            },
        ),
    ]
