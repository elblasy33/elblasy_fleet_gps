from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    gps_device_ids = fields.One2many('fleet.gps.device', 'vehicle_id', string="GPS Devices")
    gps_device_id = fields.Many2one('fleet.gps.device', compute='_compute_gps_device', string="GPS Device")
    gps_status = fields.Selection(related='gps_device_ids.status', string="GPS Status")
    gps_last_update = fields.Datetime(related='gps_device_ids.last_update', string="Last Seen")

    @api.depends('gps_device_ids')
    def _compute_gps_device(self):
        for v in self:
            v.gps_device_id = v.gps_device_ids[:1]

    def action_open_gps_device(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window', 'res_model': 'fleet.gps.device',
                'res_id': self.gps_device_id.id, 'view_mode': 'form'}
