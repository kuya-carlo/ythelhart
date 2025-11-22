import pygame

from src.prefs import Backgrounds, Constants


def setup_background(window: pygame.Surface, image_path: str = Backgrounds.MAIN_MENU):
    """Loads and scales the background image to fill the screen."""
    sw, sh = Constants.Game.SCREEN_COORDS
    img = pygame.image.load(image_path).convert()
    iw, ih = img.get_size()

    # Scale image to fit screen dimensions while maintaining aspect ratio
    scale = max(sw / iw, sh / ih)
    scaled_img = pygame.transform.smoothscale(img, (int(iw * scale), int(ih * scale)))

    # Center the scaled image
    x_offset = (scaled_img.get_width() - sw) // 2
    y_offset = (scaled_img.get_height() - sh) // 2

    # Blit the centered part of the image to the background surface
    window.blit(scaled_img, (-x_offset, -y_offset))
    return scaled_img


def draw_background(
    screen: pygame.Surface, bg_img: pygame.Surface, add_overlay: bool = True
):
    screen.blit(bg_img, (0, 0))
    if add_overlay:
        overlay = pygame.Surface(Constants.Game.SCREEN_COORDS, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
