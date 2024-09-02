"""empty message

Revision ID: d7fbd02d46a8
Revises: 
Create Date: 2024-09-01 17:22:19.177111

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d7fbd02d46a8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("birthday", sa.DateTime(), nullable=True),
        sa.Column("photo_url", sa.String(length=50), nullable=True),
        sa.Column("date_started", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chat_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("users")
    # ### end Alembic commands ###
