"""nach upgrade

Revision ID: 976eb80f973b
Revises: 
Create Date: 2025-05-08 20:55:16.689188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '976eb80f973b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('scans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=256), nullable=True),
    sa.Column('filename', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ssid', sa.String(length=128), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('force_connect', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mac', sa.String(length=17), nullable=False),
    sa.Column('manufacturer', sa.String(length=128), nullable=True),
    sa.Column('is_camera', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('stations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_stations_mac'), ['mac'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('first_seen', sa.DateTime(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('access_points',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bssid', sa.String(length=17), nullable=False),
    sa.Column('essid', sa.String(length=64), nullable=True),
    sa.Column('manufacturer', sa.String(length=128), nullable=True),
    sa.Column('is_camera', sa.Boolean(), nullable=False),
    sa.Column('counter', sa.Integer(), nullable=False),
    sa.Column('cracked_password', sa.String(length=128), nullable=True),
    sa.Column('handshake_file', sa.String(length=256), nullable=True),
    sa.Column('scan_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('access_points', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_access_points_bssid'), ['bssid'], unique=True)
        batch_op.create_index(batch_op.f('ix_access_points_scan_id'), ['scan_id'], unique=False)

    op.create_table('deauth_actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scan_id', sa.Integer(), nullable=True),
    sa.Column('mac', sa.String(length=17), nullable=False),
    sa.Column('is_client', sa.Boolean(), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('packets', sa.Integer(), nullable=False),
    sa.Column('result_file', sa.String(length=255), nullable=True),
    sa.Column('success', sa.Boolean(), nullable=False),
    sa.Column('handshake_file', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('followed_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=280), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_posts_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_posts_user_id'), ['user_id'], unique=False)

    op.create_table('scan_stations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scan_id', sa.Integer(), nullable=False),
    sa.Column('station_id', sa.Integer(), nullable=False),
    sa.Column('first_seen', sa.DateTime(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=False),
    sa.Column('power', sa.Integer(), nullable=False),
    sa.Column('packets', sa.Integer(), nullable=False),
    sa.Column('bssid', sa.String(length=17), nullable=True),
    sa.Column('probed_essids', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['station_id'], ['stations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(length=64), nullable=False),
    sa.Column('access_expiration', sa.DateTime(), nullable=False),
    sa.Column('refresh_token', sa.String(length=64), nullable=False),
    sa.Column('refresh_expiration', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tokens_access_token'), ['access_token'], unique=False)
        batch_op.create_index(batch_op.f('ix_tokens_refresh_token'), ['refresh_token'], unique=False)
        batch_op.create_index(batch_op.f('ix_tokens_user_id'), ['user_id'], unique=False)

    op.create_table('scan_access_points',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scan_id', sa.Integer(), nullable=False),
    sa.Column('access_point_id', sa.Integer(), nullable=False),
    sa.Column('first_seen', sa.DateTime(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=False),
    sa.Column('channel', sa.Integer(), nullable=False),
    sa.Column('speed', sa.Integer(), nullable=False),
    sa.Column('privacy', sa.String(length=64), nullable=True),
    sa.Column('cipher', sa.String(length=64), nullable=True),
    sa.Column('authentication', sa.String(length=64), nullable=True),
    sa.Column('power', sa.Integer(), nullable=False),
    sa.Column('beacons', sa.Integer(), nullable=False),
    sa.Column('iv', sa.Integer(), nullable=False),
    sa.Column('lan_ip', sa.String(length=45), nullable=True),
    sa.Column('id_length', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=256), nullable=True),
    sa.ForeignKeyConstraint(['access_point_id'], ['access_points.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scan_access_points')
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tokens_user_id'))
        batch_op.drop_index(batch_op.f('ix_tokens_refresh_token'))
        batch_op.drop_index(batch_op.f('ix_tokens_access_token'))

    op.drop_table('tokens')
    op.drop_table('scan_stations')
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_posts_user_id'))
        batch_op.drop_index(batch_op.f('ix_posts_timestamp'))

    op.drop_table('posts')
    op.drop_table('followers')
    op.drop_table('deauth_actions')
    with op.batch_alter_table('access_points', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_access_points_scan_id'))
        batch_op.drop_index(batch_op.f('ix_access_points_bssid'))

    op.drop_table('access_points')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('stations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_stations_mac'))

    op.drop_table('stations')
    op.drop_table('settings')
    op.drop_table('scans')
    # ### end Alembic commands ###
