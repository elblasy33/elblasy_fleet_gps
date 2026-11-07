import hmac
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
MAX_BODY = 5 * 1024 * 1024


class GpsPush(http.Controller):

    @http.route('/fleet_gps/push/<string:token>', type='http', auth='public', methods=['POST'],
                csrf=False, save_session=False)
    def push(self, token, **_kw):
        """Receives Traccar's forward.url (``forward.json=true``): one ``{"position":…, "device":…}`` object,
        or a list of them. Several databases: send the X-Odoo-Database header (Traccar forward.header)."""
        raw = request.httprequest.get_data()
        if len(raw) > MAX_BODY:
            return request.make_json_response({'error': 'too large'}, status=413)
        server = request.env['fleet.gps.server'].sudo().search([('push_token', '=', token)], limit=1)
        if not server or not hmac.compare_digest(server.push_token, token):
            return request.make_json_response({'error': 'not found'}, status=404)
        try:
            data = json.loads(raw)
        except ValueError:
            return request.make_json_response({'error': 'invalid json'}, status=400)
        items = data if isinstance(data, list) else [data]
        positions, devices = [], {}
        for it in items:
            if not isinstance(it, dict):
                continue
            pos = it.get('position') if isinstance(it.get('position'), dict) else (it if 'deviceId' in it else None)
            if pos:
                positions.append(pos)
            dev = it.get('device')
            if isinstance(dev, dict) and dev.get('id'):
                devices[dev['id']] = dev
        stored = request.env['fleet.gps.position'].sudo()._ingest(server, positions, devices)
        if devices:
            request.env['fleet.gps.device'].sudo()._apply_device_status(server, list(devices.values()))
        return request.make_json_response({'ok': True, 'stored': stored})

    @http.route('/fleet_gps/event/<string:token>', type='http', auth='public', methods=['POST'],
                csrf=False, save_session=False)
    def event(self, token, **_kw):
        """Traccar's event.forward.url (``event.forward.json=true``): ``{"event":…, "device":…, "position":…, "geofence":…}``
        (or a list of them)."""
        raw = request.httprequest.get_data()
        if len(raw) > MAX_BODY:
            return request.make_json_response({'error': 'too large'}, status=413)
        server = request.env['fleet.gps.server'].sudo().search([('push_token', '=', token)], limit=1)
        if not server or not hmac.compare_digest(server.push_token, token):
            return request.make_json_response({'error': 'not found'}, status=404)
        try:
            data = json.loads(raw)
        except ValueError:
            return request.make_json_response({'error': 'invalid json'}, status=400)
        events, positions = [], {}
        for it in data if isinstance(data, list) else [data]:
            if not isinstance(it, dict):
                continue
            ev = it.get('event') if isinstance(it.get('event'), dict) else (it if 'type' in it and 'deviceId' in it else None)
            if ev:
                events.append(ev)
            pos = it.get('position')
            if isinstance(pos, dict) and pos.get('id'):
                positions[pos['id']] = pos
        stored = request.env['fleet.gps.event'].sudo()._ingest(server, events, positions=positions)
        return request.make_json_response({'ok': True, 'stored': stored})
