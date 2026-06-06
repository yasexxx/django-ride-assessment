"""Project-wide constants"""

# WGS84: the standard GPS latitude/longitude spatial reference system. Used for
# every PointField and Point() construction so the SRID is declared exactly once.
WGS84_SRID = 4326

# Valid WGS84 coordinate bounds (degrees) — used to validate GPS query params.
LATITUDE_MIN, LATITUDE_MAX = -90.0, 90.0
LONGITUDE_MIN, LONGITUDE_MAX = -180.0, 180.0
