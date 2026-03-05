#Camerahelper:convertsworldcoordinatesintoview/screencoordinates
import pygame

class Camera:
    def __init__(self, screen_w, screen_h, zoom=1.0):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.zoom = zoom
        self.x = 0
        self.y = 0

    def follow(self, target_rect: pygame.Rect, world_w: int, world_h: int):
        #Centercameraontargetthenclampsoyoucantscrollpastworldedges
        view_w = self.screen_w / self.zoom
        view_h = self.screen_h / self.zoom

        self.x = target_rect.centerx - view_w / 2
        self.y = target_rect.centery - view_h / 2

        self.x = max(0, min(self.x, world_w - view_w))
        self.y = max(0, min(self.y, world_h - view_h))

    def apply_pos(self, world_x, world_y):
        sx = (world_x - self.x) * self.zoom
        sy = (world_y - self.y) * self.zoom
        return sx, sy

    def apply_rect(self, rect: pygame.Rect):
        sx, sy = self.apply_pos(rect.x, rect.y)
        return pygame.Rect(sx, sy, rect.width * self.zoom, rect.height * self.zoom)