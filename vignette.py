import pygame
import numpy as np

def create_vignette(width, height, strength=120):
    cx, cy = width / 2, height / 2
    max_dist = np.sqrt(cx**2 + cy**2)

    y_coords, x_coords = np.mgrid[0:height, 0:width]
    dist = np.sqrt((x_coords - cx)**2 + (y_coords - cy)**2)
    alpha = np.clip((dist / max_dist) ** 2 * strength, 0, 255).astype(np.uint8)

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    alpha_array = pygame.surfarray.pixels_alpha(surface)
    alpha_array[:] = alpha.T  # transpose because surfarray is x,y not y,x
    del alpha_array

    return surface