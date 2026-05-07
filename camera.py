import math

class Camera:
    """Smooth camera that follows a target using frame-rate independent lerp."""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
        self.smoothing = 8.0  # higher = stiffer / faster catch-up

    def update(self, target, dt):
        """Lerp toward target position using dt for frame-rate independence."""
        t = 1.0 - math.exp(-self.smoothing * dt)
        self.x += (target.position.x - self.x) * t
        self.y += (target.position.y - self.y) * t
