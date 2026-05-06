class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

    def update(self, target, screen_width, screen_height):
        self.x = target.position.x - screen_width // 2
        self.y = target.position.y - screen_height // 2
