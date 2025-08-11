import pygame
import sys
import random
import cv2
import numpy as np
from enum import Enum

class GameMode(Enum):
    CLASSIC = 1
    CHAOS = 2
    GRAVITY = 3
    PULSE = 4

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Bouncing Ball Game")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

        self.circle_center = (self.width // 2, self.height // 2)
        self.circle_radius = 250
        self.max_ball_radius = self.circle_radius - 10

        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 36)

        self.is_recording = False
        self.video_writer = None

        self.game_mode = GameMode.CLASSIC

    def reset(self):
        self.bounce_count = 0
        self.balls = []
        self.speed_increase = 1.015

        if self.game_mode == GameMode.CLASSIC:
            self.balls.append(self.create_ball())
        elif self.game_mode == GameMode.CHAOS:
            for _ in range(10):
                self.balls.append(self.create_ball())
        elif self.game_mode == GameMode.GRAVITY:
            self.balls.append(self.create_ball(velocity=[random.uniform(-5, 5), 0]))
            self.gravity = pygame.Vector2(0, 0.2)
        elif self.game_mode == GameMode.PULSE:
            self.balls.append(self.create_ball())
            self.pulse_speed = 1
            self.min_circle_radius = 150
            self.max_circle_radius = 250
            self.circle_radius = self.max_circle_radius

    def create_ball(self, position=None, velocity=None, radius=20, color=None):
        return {
            'pos': pygame.Vector2(position if position else [self.width // 2, self.height // 2]),
            'vel': pygame.Vector2(velocity if velocity else [random.choice([-5, 5]), random.choice([-5, 5])]),
            'radius': radius,
            'color': color if color else random.choice(self.colors)
        }

    def toggle_recording(self):
        self.is_recording = not self.is_recording
        if self.is_recording:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter('gameplay.avi', fourcc, 60.0, (self.width, self.height))
            print("Recording started.")
        else:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            print("Recording stopped.")

    def display_menu(self):
        title_text = self.font_large.render("Select a Game Mode", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 200))

        button_texts = ["Classic", "Chaos", "Gravity", "Pulse"]
        buttons = []
        for i, text in enumerate(button_texts):
            button_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 - 100 + i * 70, 300, 50)
            buttons.append(button_rect)

        while True:
            self.screen.fill(self.BLACK)
            self.screen.blit(title_text, title_rect)

            for i, rect in enumerate(buttons):
                pygame.draw.rect(self.screen, self.WHITE, rect)
                button_text = self.font_medium.render(button_texts[i], True, self.BLACK)
                text_rect = button_text.get_rect(center=rect.center)
                self.screen.blit(button_text, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(buttons):
                        if rect.collidepoint(event.pos):
                            self.game_mode = list(GameMode)[i]
                            self.reset()
                            return

    def display_end_screen(self):
        text = self.font_large.render("Game Over", True, self.WHITE)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 100))

        play_again_button = pygame.Rect(self.width // 2 - 150, self.height // 2, 140, 50)
        menu_button = pygame.Rect(self.width // 2 + 10, self.height // 2, 140, 50)

        while True:
            self.screen.fill(self.BLACK)
            self.screen.blit(text, text_rect)

            pygame.draw.rect(self.screen, self.WHITE, play_again_button)
            pygame.draw.rect(self.screen, self.WHITE, menu_button)

            play_again_text = self.font_medium.render("Play Again", True, self.BLACK)
            menu_text = self.font_medium.render("Menu", True, self.BLACK)
            self.screen.blit(play_again_text, play_again_text.get_rect(center=play_again_button.center))
            self.screen.blit(menu_text, menu_text.get_rect(center=menu_button.center))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.collidepoint(event.pos):
                        self.reset()
                        return
                    elif menu_button.collidepoint(event.pos):
                        self.display_menu()
                        return

    def update(self):
        if self.game_mode == GameMode.PULSE:
            self.circle_radius += self.pulse_speed
            if self.circle_radius > self.max_circle_radius or self.circle_radius < self.min_circle_radius:
                self.pulse_speed *= -1

        for ball in self.balls:
            if self.game_mode == GameMode.GRAVITY:
                ball['vel'] += self.gravity

            ball['pos'] += ball['vel']

            dist_to_center = ball['pos'].distance_to(self.circle_center)

            if dist_to_center + ball['radius'] >= self.circle_radius:
                normal = (ball['pos'] - pygame.Vector2(self.circle_center)).normalize()
                ball['vel'] = ball['vel'].reflect(normal)

                if self.game_mode != GameMode.GRAVITY:
                    ball['vel'] *= self.speed_increase

                ball['pos'] = pygame.Vector2(self.circle_center) + normal * (self.circle_radius - ball['radius'])

                self.bounce_count += 1

                if self.game_mode == GameMode.CLASSIC:
                    if ball['radius'] < self.max_ball_radius:
                        ball['radius'] += 1
                        ball['color'] = random.choice(self.colors)
                    else:
                        self.display_end_screen()

    def draw(self):
        self.screen.fill(self.BLACK)
        pygame.draw.circle(self.screen, self.WHITE, self.circle_center, self.circle_radius, 2)

        for ball in self.balls:
            pygame.draw.circle(self.screen, ball['color'], (int(ball['pos'].x), int(ball['pos'].y)), ball['radius'])

        bounce_text = self.font_small.render(f"Bounces: {self.bounce_count}", True, self.WHITE)
        self.screen.blit(bounce_text, (10, 10))

        if self.is_recording:
            pygame.draw.circle(self.screen, (255, 0, 0), (self.width - 30, 30), 10)

        if self.is_recording and self.video_writer:
            frame = pygame.surfarray.array3d(self.screen)
            frame = frame.transpose([1, 0, 2])
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.video_writer.write(frame)

        pygame.display.flip()

    def run(self):
        while True:
            self.display_menu()

            running = True
            clock = pygame.time.Clock()

            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.toggle_recording()

                self.update()
                self.draw()
                clock.tick(60)

                # A bit of a hack to break out of the inner loop
                if self.game_mode == GameMode.CLASSIC and self.balls and self.balls[0]['radius'] >= self.max_ball_radius:
                    self.display_end_screen()
                    running = False # This will break the inner loop and go to the outer one (main menu)

            if self.is_recording:
                self.toggle_recording()
