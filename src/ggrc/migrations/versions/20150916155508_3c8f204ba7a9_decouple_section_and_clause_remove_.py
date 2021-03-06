# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: jost@reciprocitylabs.com
# Maintained By: jost@reciprocitylabs.com

"""Decouple section and clause, remove directive foreign key, remove type

Revision ID: 3c8f204ba7a9
Revises: 29dca3ce0556
Create Date: 2015-09-16 15:55:08.889667

"""

# revision identifiers, used by Alembic.
revision = '3c8f204ba7a9'
down_revision = '39be15719884'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from ggrc.models.background_task import create_task
from ggrc.fulltext import get_indexer
from ggrc.fulltext.recordbuilder import fts_record_for
from ggrc.fulltext.recordbuilder import model_is_indexed
from ggrc.models import all_models
from ggrc.app import db
from ggrc.views import generate_query_chunks


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clauses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('na', sa.Boolean(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('os_state', sa.String(length=250), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('url', sa.String(length=250), nullable=True),
    sa.Column('reference_url', sa.String(length=250), nullable=True),
    sa.Column('secondary_contact_id', sa.Integer(), nullable=True),
    sa.Column('contact_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=250), nullable=False),
    sa.Column('slug', sa.String(length=250), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('modified_by_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('context_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=250), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['contact_id'], ['people.id'], ),
    sa.ForeignKeyConstraint(['context_id'], ['contexts.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['clauses.id'], ),
    sa.ForeignKeyConstraint(['secondary_contact_id'], ['people.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug', name='uq_clauses')
    )
    # move clauses to a stand alone table
    sql = """
    INSERT INTO clauses (
      na, notes, os_state, parent_id, description,
      url, reference_url, secondary_contact_id, contact_id,
      title, slug, created_at, modified_by_id, updated_at, context_id,
      status, end_date, start_date
    )
    SELECT na, notes, os_state, parent_id, description,
         url, reference_url, secondary_contact_id, contact_id,
         title, slug, created_at, modified_by_id, updated_at, context_id,
         status, end_date, start_date
    FROM sections
    WHERE type = 'Clause'
    """
    op.execute(sql)

    # remove clauses from the sections table
    sql = """
    DELETE
    FROM sections
    WHERE type = 'Clause'
    """
    op.execute(sql)

    sql = """
    REPLACE INTO relationships (
      modified_by_id, created_at, updated_at, source_id,
      source_type, destination_id, destination_type, context_id
    )
    SELECT dc.modified_by_id, dc.created_at, dc.updated_at,
         dc.id as source_id, 'Section' as source_type,
         dc.directive_id as destination_id,
         d.meta_kind as destination_type,
         dc.context_id
    FROM sections as dc JOIN directives as d ON dc.directive_id = d.id;
    """
    op.execute(sql)

    # remove foreign key constraint
    op.drop_constraint(
        'sections_ibfk_1',
        'sections',
        type_='foreignkey')

    op.drop_column('sections', 'directive_id')

    op.drop_column('sections', 'type')

    indexer = get_indexer()
    indexer.delete_records_by_type('Clause', False)
    indexer.delete_records_by_type('Section', False)
    models = [
        all_models.Section,
        all_models.Clause
    ]
    models = [model for model in models if model_is_indexed(model)]

    for model in models:
        mapper_class = model._sa_class_manager.mapper.base_mapper.class_
        query = model.query.options(
            db.undefer_group(mapper_class.__name__ + '_complete'),
        )
        for query_chunk in generate_query_chunks(query):
            for instance in query_chunk:
                indexer.create_record(fts_record_for(instance), False)
        db.session.commit()


def downgrade():
    op.add_column('sections', sa.Column('type', mysql.VARCHAR(length=250), nullable=True))
    # add the foreign key back.
    op.add_column(
        'sections',
        sa.Column(
            'directive_id',
            mysql.INTEGER(display_width=11),
            sa.ForeignKey('directives.id', name='sections_ibfk_1'),
            autoincrement=False,
            nullable=True
        )
    )
    sql = """
    UPDATE sections
    SET type = 'Section'
    """
    op.execute(sql)

    # TODO: WILL THIS BREAK ANY MAPPINGS? ID-s ARE DIFFERENT ON DOWNGRADE!
    sql = """
    INSERT INTO sections (
      type, na, notes, os_state, parent_id, description,
      url, reference_url, secondary_contact_id, contact_id,
      title, slug, created_at, modified_by_id, updated_at, context_id,
      status, end_date, start_date
    )
    SELECT 'Clause', na, notes, os_state, parent_id, description,
         url, reference_url, secondary_contact_id, contact_id,
         title, slug, created_at, modified_by_id, updated_at, context_id,
         status, end_date, start_date
    FROM clauses
    """
    op.execute(sql)
    op.drop_table('clauses')
