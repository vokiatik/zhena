"""monthly_report_tables_rewrite

Drops the old retail/dictionary tables and creates the new
advertisement-centric structure for the monthly report workflow.

Revision ID: i6j7k8l9m0n1
Revises: h5i6j7k8l9m0
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'i6j7k8l9m0n1'
down_revision: Union[str, Sequence[str], None] = 'ca6a655d9b18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    # ── Drop old tables (order matters for FK deps) ──────────────────────
    op.execute("DROP TABLE IF EXISTS analyst_processed CASCADE")
    op.execute("DROP TABLE IF EXISTS retail_processed CASCADE")
    op.execute("DROP TABLE IF EXISTS retail CASCADE")
    op.execute("DROP TABLE IF EXISTS picture_attribute_reference CASCADE")
    op.execute("DROP TABLE IF EXISTS picture_attribute_reference_type CASCADE")
    op.execute("DROP TABLE IF EXISTS ecom_format_for_detector CASCADE")
    op.execute("DROP TABLE IF EXISTS ecom_format CASCADE")
    op.execute("DROP TABLE IF EXISTS funnel_stage CASCADE")

    # ── New dictionary tables ────────────────────────────────────────────

    op.create_table(
        'simple_value_type',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('field_name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
        sa.UniqueConstraint('field_name'),
    )

    op.create_table(
        'simple_value',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('column_name_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'format',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('retailer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('format', sa.Text(), nullable=True),
        sa.Column('funnel_stage_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sov', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'detector_format_comparison',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('detector_format', sa.Text(), nullable=True),
        sa.Column('format_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    # Seed simple_value_type with the seven standard categories
    op.execute("""
        INSERT INTO simple_value_type (id, field_name)
        VALUES
            (gen_random_uuid(), 'advertiser'),
            (gen_random_uuid(), 'brand'),
            (gen_random_uuid(), 'add_category'),
            (gen_random_uuid(), 'product_category'),
            (gen_random_uuid(), 'brand_category'),
            (gen_random_uuid(), 'retailer_clean'),
            (gen_random_uuid(), 'funnel_stage')
        ON CONFLICT (field_name) DO NOTHING
    """)

    # ── New data tables ──────────────────────────────────────────────────

    op.create_table(
        'advertisement',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('process_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('retailer_clean_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('advertiser_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('product_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('brand_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('first_appearance_date', sa.Date(), nullable=True),
        sa.Column('last_appearance_date', sa.Date(), nullable=True),
        sa.Column('data_type', sa.Text(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('declined', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'advertisement_link',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('add_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('link', sa.Text(), nullable=True),
        sa.Column('appearance_period', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'advertisement_brand',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('add_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'advertisement_category',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('add_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'advertisement_format',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('add_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('format_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'advertisement_add_category',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('add_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('add_category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'advertisement_price',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('add_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    op.create_table(
        'advertisement_bools',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('add_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_player', sa.Boolean(), nullable=True),
        sa.Column('referent_market', sa.Boolean(), nullable=True),
        sa.Column('packed_chocolate', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('now()')),
    )

    # Update process_types: data_prep now targets advertisement
    op.execute("""
        UPDATE process_types
        SET table_name = 'advertisement'
        WHERE process_type_name = 'data_prep'
    """)

    # Add table_admin_settings rows for new tables
    op.execute("""
        INSERT INTO table_admin_settings (id, table_name, display_name, visible, only_admin, editable)
        VALUES
            (gen_random_uuid(), 'simple_value_type', 'Simple Value Types', true, true, true),
            (gen_random_uuid(), 'simple_value', 'Simple Values', true, true, true),
            (gen_random_uuid(), 'format', 'Formats', true, true, true),
            (gen_random_uuid(), 'detector_format_comparison', 'Detector Format Comparison', true, true, true)
        ON CONFLICT (table_name) DO NOTHING
    """)

    # Remove old table_admin_settings rows
    op.execute("""
        DELETE FROM table_admin_settings
        WHERE table_name IN (
            'funnel_stage', 'ecom_format', 'ecom_format_for_detector',
            'retail', 'picture_attribute_reference', 'picture_attribute_reference_type'
        )
    """)


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS advertisement_bools CASCADE")
    op.execute("DROP TABLE IF EXISTS advertisement_price CASCADE")
    op.execute("DROP TABLE IF EXISTS advertisement_add_category CASCADE")
    op.execute("DROP TABLE IF EXISTS advertisement_format CASCADE")
    op.execute("DROP TABLE IF EXISTS advertisement_category CASCADE")
    op.execute("DROP TABLE IF EXISTS advertisement_brand CASCADE")
    op.execute("DROP TABLE IF EXISTS advertisement_link CASCADE")
    op.execute("DROP TABLE IF EXISTS advertisement CASCADE")
    op.execute("DROP TABLE IF EXISTS detector_format_comparison CASCADE")
    op.execute("DROP TABLE IF EXISTS format CASCADE")
    op.execute("DROP TABLE IF EXISTS simple_value CASCADE")
    op.execute("DROP TABLE IF EXISTS simple_value_type CASCADE")
