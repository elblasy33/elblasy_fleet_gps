"""Trips, stops and day totals computed from raw GPS positions (no ORM: pure functions, unit-testable).

A port of Tracar's analytics (lib/analytics.ts). Traccar's own summary/trips use the odometer, which resets on many
installs (negative distances, maxSpeed 0), so everything is recomputed from the stored positions.
"""
import math

STOP_MIN_MS = 3 * 60000     # standing still this long is a stop
TRIP_MIN_M = 200            # shorter movements are GPS drift, not a trip
GAP_MS = 10 * 60000         # no data for this long ends the trip / stop
MAX_KMH = 220               # faster than this is a GPS glitch, not driving
MOVING_KMH = 3
HARSH_KMH_S = 8             # km/h gained or lost per second that counts as harsh acceleration / braking
SPEED_BINS = ((3, 0), (30, 1), (60, 2), (90, 3), (120, 4))  # upper bound (km/h) -> bin; above -> 5


def haversine(lat1, lon1, lat2, lon2):
    r = math.pi / 180
    d_lat, d_lon = (lat2 - lat1) * r, (lon2 - lon1) * r
    x = math.sin(d_lat / 2) ** 2 + math.cos(lat1 * r) * math.cos(lat2 * r) * math.sin(d_lon / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(x))


def _bin(kmh):
    for upper, idx in SPEED_BINS:
        if kmh < upper:
            return idx
    return 5


def empty_day():
    return {
        'dist': 0.0, 'max_speed': 0.0, 'moving_ms': 0, 'idle_ms': 0, 'stop_ms': 0, 'speed_sum': 0.0,
        'hour_dist': [0.0] * 24, 'hour_moving': [0] * 24, 'hist': [0] * 6,
        'over_ms': 0, 'over_count': 0, 'harsh_brake': 0, 'harsh_accel': 0, 'trips': 0, 'points': 0,
        'trip_list': [], 'stop_list': [],
    }


def compute(positions, limit_kmh, hour_of):
    """``positions``: dicts / tuples sorted by fix time: (ms, lat, lon, kmh, ignition). ``hour_of(ms)`` -> local hour 0-23.
    Returns the day totals plus ``trip_list`` and ``stop_list`` (times in ms)."""
    g = empty_day()
    ps = [p for p in positions if p[1] != 0 or p[2] != 0]
    g['points'] = len(ps)
    trip = None
    pend = None
    stop = None
    last_brake = last_accel = 0
    over_active = False

    def end_trip():
        nonlocal trip
        if trip and trip['dist'] >= TRIP_MIN_M:
            g['trip_list'].append({
                's': trip['s'], 'e': trip['e'], 's_lat': trip['s_lat'], 's_lon': trip['s_lon'],
                'e_lat': trip['e_lat'], 'e_lon': trip['e_lon'], 'dist': trip['dist'], 'max': trip['max'],
                'avg': trip['spd'] / trip['mov'] if trip['mov'] else 0.0, 'mov': trip['mov']})
        trip = None

    def end_stop():
        nonlocal stop
        if stop and stop['e'] - stop['s'] >= STOP_MIN_MS:
            g['stop_list'].append(stop)
        stop = None

    for i in range(1, len(ps)):
        ta, lat_a, lon_a, kmh_a, ign_a = ps[i - 1]
        tb, lat_b, lon_b, kmh_b, _ign_b = ps[i]
        dt = tb - ta
        if dt <= 0:
            continue
        ok_a, ok_b = kmh_a < MAX_KMH, kmh_b < MAX_KMH
        if ok_b:
            g['max_speed'] = max(g['max_speed'], kmh_b)
        if dt > GAP_MS:  # data gap
            end_trip()
            end_stop()
            pend = None
            continue
        hour = hour_of(ta)
        d = haversine(lat_a, lon_a, lat_b, lon_b)
        implied = d / (dt / 1000) * 3.6
        moving = ok_a and kmh_a >= MOVING_KMH
        if moving:
            g['moving_ms'] += dt
            g['hour_moving'][hour] += dt
            g['speed_sum'] += kmh_a * dt
            dd = d if implied <= MAX_KMH and d < 5000 else 0
            g['dist'] += dd
            g['hour_dist'][hour] += dd
            end_stop()
            pend = None
            if not trip:
                trip = {'s': ta, 'e': tb, 's_lat': lat_a, 's_lon': lon_a, 'e_lat': lat_b, 'e_lon': lon_b,
                        'dist': 0.0, 'max': 0.0, 'mov': 0, 'spd': 0.0}
            trip.update(e=tb, e_lat=lat_b, e_lon=lon_b)
            trip['dist'] += dd
            trip['mov'] += dt
            trip['spd'] += kmh_a * dt
            if ok_b:
                trip['max'] = max(trip['max'], kmh_b)
        else:
            g['idle_ms' if ign_a else 'stop_ms'] += dt
            if not pend and not stop:
                pend = {'t': ta, 'lat': lat_a, 'lon': lon_a, 'ign': bool(ign_a)}
            if pend and tb - pend['t'] >= STOP_MIN_MS:
                end_trip()
                if not stop:
                    stop = {'s': pend['t'], 'e': tb, 'lat': pend['lat'], 'lon': pend['lon'], 'ign': pend['ign']}
            if stop:
                stop['e'] = tb
        g['hist'][_bin(kmh_a)] += dt
        if ok_a and kmh_a > limit_kmh:
            g['over_ms'] += dt
            if not over_active:
                g['over_count'] += 1
                over_active = True
        else:
            over_active = False
        if dt <= 15000 and ok_a and ok_b:
            acc = (kmh_b - kmh_a) / (dt / 1000)  # km/h per second
            if acc <= -HARSH_KMH_S and kmh_a >= 20 and tb - last_brake > 5000:
                g['harsh_brake'] += 1
                last_brake = tb
            if acc >= HARSH_KMH_S and tb - last_accel > 5000:
                g['harsh_accel'] += 1
                last_accel = tb
    end_trip()
    end_stop()
    g['trips'] = len(g['trip_list'])
    return g


def driver_score(dist_m, moving_ms, over_ms, harsh):
    """0-100 from the share of moving time over the limit and harsh events per 100 km."""
    km = max(dist_m / 1000, 1)
    over_share = over_ms / moving_ms if moving_ms else 0
    return max(0, round(100 - over_share * 60 - min(harsh / km * 100 * 3, 40)))
