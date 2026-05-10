import math

class Camera:
    """Smooth camera that follows a target using frame-rate independent lerp."""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
        self.smoothing = 4.0  # higher = stiffer / faster catch-up

    def update(self, target, dt, map_w, map_h, screen_w, screen_h, zoom):
        """Lerp toward target position using dt for frame-rate independence."""
        t = 1.0 - math.exp(-self.smoothing * dt)

        self.x += (target.position.x - self.x) * t
        self.y += (target.position.y - self.y) * t

        if map_w <= 0 or map_h <= 0:
            return

        half_w = screen_w / (2 * zoom)
        half_h = screen_h / (2 * zoom)

        # Clamp so viewport never shows past map edges
        min_x = half_w
        max_x = map_w - half_w
        min_y = half_h
        max_y = map_h - half_h

        if max_x < min_x:
            max_x = min_x = map_w / 2
        if max_y < min_y:
            max_y = min_y = map_h / 2

        self.x = max(min_x, min(max_x, self.x))
        self.y = max(min_y, min(max_y, self.y))

