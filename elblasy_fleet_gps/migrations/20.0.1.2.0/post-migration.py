from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Stops stored before the ``place`` column existed get their geofence / rounded position."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['fleet.gps.stop']._assign_places()
