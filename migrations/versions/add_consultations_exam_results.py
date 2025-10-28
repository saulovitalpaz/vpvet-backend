"""Add consultations and exam_results tables

Revision ID: 4b3d4e674b26
Revises: 3a2c2b563a15
Create Date: 2025-10-18 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4b3d4e674b26'
down_revision = '3a2c2b563a15'
branch_labels = None
depends_on = None


def upgrade():
    # Create consultations table
    op.create_table('consultations',
    sa.Column('appointment_id', sa.UUID(), nullable=False),
    sa.Column('chief_complaint', sa.Text(), nullable=True),
    sa.Column('physical_exam', sa.Text(), nullable=True),
    sa.Column('diagnosis', sa.Text(), nullable=True),
    sa.Column('prognosis', sa.String(length=50), nullable=True),
    sa.Column('treatment_plan', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('appointment_id')
    )

    # Create exam_results table
    op.create_table('exam_results',
    sa.Column('consultation_id', sa.UUID(), nullable=False),
    sa.Column('animal_id', sa.UUID(), nullable=False),
    sa.Column('exam_type', sa.String(length=100), nullable=False),
    sa.Column('access_code', sa.String(length=20), nullable=False),
    sa.Column('findings', sa.Text(), nullable=False),
    sa.Column('impression', sa.Text(), nullable=False),
    sa.Column('pdf_url', sa.Text(), nullable=True),
    sa.Column('images_url', postgresql.ARRAY(sa.Text()), nullable=True),
    sa.Column('exam_date', sa.Date(), nullable=False),
    sa.Column('last_accessed', sa.DateTime(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['animal_id'], ['animals.id'], ),
    sa.ForeignKeyConstraint(['consultation_id'], ['consultations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('access_code')
    )


def downgrade():
    op.drop_table('exam_results')
    op.drop_table('consultations')
