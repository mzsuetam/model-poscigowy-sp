import math


def polar_to_cartesian(r, theta_deg) -> tuple[float, float]:
    theta_rad = math.radians(theta_deg)

    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)

    return x, y


def cartesian_to_polar(x, y) -> tuple[float, float]:
    r = math.sqrt(x * x + y * y)
    theta_rad = math.atan2(y, x)
    theta_deg = math.degrees(theta_rad)

    return r, theta_deg


def calc_end_line(origin, angle, length):
    x = origin[0] + length * math.cos(math.radians(angle))
    y = origin[1] + length * math.sin(math.radians(angle))
    return x, y


def calc_euclidean_dist(point_1, point_2) -> float:
    return math.sqrt(math.pow((abs(point_2[0] - point_1[0])), 2) +
                     math.pow((abs(point_2[1] - point_1[1])), 2))
