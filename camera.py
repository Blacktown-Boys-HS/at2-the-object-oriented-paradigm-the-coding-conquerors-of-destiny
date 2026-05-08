import math

class Camera:
    """Smooth camera that follows a target using frame-rate independent lerp."""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
        self.smoothing = 8.0  # higher = stiffer / faster catch-up

    def update(self, target, dt, map_w, map_h, screen_w, screen_h, zoom):
        """Lerp toward target position using dt for frame-rate independence."""
        t = 1.0 - math.exp(-self.smoothing * dt)

        self.x += (target.position.x - self.x) * t
        self.y += (target.position.y - self.y) * t

        half_w = screen_w / (2 * zoom)
        half_h = screen_h / (2 * zoom)

        self.x = max(half_w, min(map_w - half_w, self.x))
        self.y = max(half_h, min(map_h - half_h, self.y))

