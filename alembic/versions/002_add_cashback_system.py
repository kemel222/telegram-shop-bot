"""Add cashback system and remove referrals

Revision ID: 002
Revises: 001
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Удаляем таблицу referrals
    op.drop_table('referrals')
    
    # Создаем таблицу cashback_transactions
    op.create_table('cashback_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('cashback_percent', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Обновляем таблицу users
    op.drop_column('users', 'referral_code')
    op.drop_column('users', 'referred_by_id')
    op.drop_column('users', 'is_first_purchase')
    op.add_column('users', sa.Column('cashback_balance', sa.Float(), nullable=True, default=0.0))
    
    # Обновляем таблицу categories
    op.add_column('categories', sa.Column('cashback_percent', sa.Float(), nullable=True, default=3.5))


def downgrade():
    # Откатываем изменения
    op.drop_column('categories', 'cashback_percent')
    op.drop_column('users', 'cashback_balance')
    op.add_column('users', sa.Column('is_first_purchase', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('referred_by_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('referral_code', mysql.VARCHAR(length=50), nullable=True))
    
    op.drop_table('cashback_transactions')
    
    op.create_table('referrals',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('referrer_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('referred_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('bonus_earned', mysql.FLOAT(), nullable=True),
        sa.Column('order_id', mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('created_at', mysql.DATETIME(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name='referrals_ibfk_3'),
        sa.ForeignKeyConstraint(['referrer_id'], ['users.id'], name='referrals_ibfk_1'),
        sa.ForeignKeyConstraint(['referred_id'], ['users.id'], name='referrals_ibfk_2'),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

