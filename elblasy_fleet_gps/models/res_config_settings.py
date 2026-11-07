from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gps_speed_limit = fields.Integer("Speed Limit (km/h)", config_parameter='elblasy_fleet_gps.speed_limit', default=80)
    gps_retention_days = fields.Integer("Keep Raw Positions (days)", config_parameter='elblasy_fleet_gps.retention_days', default=30)
    gps_color_moving = fields.Char("Moving", config_parameter='elblasy_fleet_gps.color_moving', default='#23e76a')
    gps_color_idle = fields.Char("Idling", config_parameter='elblasy_fleet_gps.color_idle', default='#f59e0b')
    gps_color_stopped = fields.Char("Stopped", config_parameter='elblasy_fleet_gps.color_stopped', default='#27aef1')
    gps_color_over = fields.Char("Over speed limit", config_parameter='elblasy_fleet_gps.color_over', default='#f20202')
    gps_color_offline = fields.Char("Offline", config_parameter='elblasy_fleet_gps.color_offline', default='#727374')
    gps_timezone = fields.Char("Reports Timezone", config_parameter='elblasy_fleet_gps.timezone', default='Africa/Cairo',
                               help="Days in the reports start at midnight of this timezone (e.g. Africa/Cairo).")
    gps_geocoding = fields.Boolean("Street addresses (OpenStreetMap)", config_parameter='elblasy_fleet_gps.geocoding',
                                   help="Show the street address of a vehicle. Sends its coordinates to the public Nominatim service.")
    gps_icon_size = fields.Integer("Vehicle icon size (%)", config_parameter='elblasy_fleet_gps.icon_size', default=140,
                                   help="Size of the vehicles on the live map and the playback, in percent (50-250).")
