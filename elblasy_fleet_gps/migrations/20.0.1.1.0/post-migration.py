def migrate(cr, version):
    """The poll cron is noupdate, so databases installed with the 5-minute interval keep it unless changed here.
    It now runs every minute and decides by itself whether Traccar is already pushing. Plain SQL on purpose: writing a
    cron through the ORM tries to lock its row and fails while the cron worker holds it ("could not serialize access")."""
    cr.execute("""
        UPDATE ir_cron SET interval_number = 1, interval_type = 'minutes'
         WHERE id IN (SELECT res_id FROM ir_model_data
                       WHERE module = 'elblasy_fleet_gps' AND name = 'cron_gps_poll' AND model = 'ir.cron')""")
