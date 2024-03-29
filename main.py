import math
import pygame
import os
from collections import deque
from random import randint
from pygame.locals import *

FPS = 60
SCREEN_WIDTH = 550
SCREEN_HEIGHT = 500
ANIMATION_SPEED = 0.1


class Bird(pygame.sprite.Sprite):
    WIDTH = HEIGHT = 32
    SINK_SPEED = 0.12
    CLIMB_SPEED = 0.19
    CLIMB_DURATION = 400

    def __init__(self, free_fall_time, images):

        super(Bird, self).__init__()

        # set bird attributes
        self.x, self.y = int(SCREEN_WIDTH * 0.15), int(SCREEN_HEIGHT / 2)
        self.free_fall_time = free_fall_time
        self._wing_up_, self._wing_down_ = images
        self._mask_wingup = pygame.mask.from_surface(self._wing_up_)
        self._mask_wingdown = pygame.mask.from_surface(self._wing_down_)

    def update(self, delta_frames=1):
        # update bird frame

        # if bird is allowed to fall free without any intervention
        if self.free_fall_time > 0:

            frac_climb_done = 1 - self.free_fall_time / Bird.CLIMB_DURATION
            self.y -= (Bird.CLIMB_SPEED * conversions.frames_to_msec(delta_frames) *
                       (1 - math.cos(frac_climb_done * math.pi)))

            self.free_fall_time -= conversions.frames_to_msec(delta_frames)
        else:
            self.y += Bird.SINK_SPEED * conversions.frames_to_msec(delta_frames)

    @property
    def animate(self):
        # switches bird's wing up and down images depending on milliseconds
        if pygame.time.get_ticks() % 31 >= 4:
            return self._wing_up_
        else:
            return self._wing_down_

    @property
    def mask(self):
        """Get a bitmask for use in collision detection.

        The bitmask excludes all pixels in self.image with a
        transparency greater than 127."""
        if pygame.time.get_ticks() % 500 >= 250:
            return self._mask_wingup
        else:
            return self._mask_wingdown

    @property
    def rect(self):
        """Get the bird's position, width, and height, as a pygame.Rect."""
        return Rect(self.x, self.y, Bird.WIDTH, Bird.HEIGHT)


class PipePair(pygame.sprite.Sprite):s

    WIDTH = 80
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 3500

    def __init__(self, pipes_images):

        # print(pipes_images)
        pipe_end_img, pipe_body_img = pipes_images
        self.x = float(SCREEN_WIDTH - 1)
        self.score_count = False

        self.image = pygame.Surface((PipePair.WIDTH, SCREEN_HEIGHT), SRCALPHA)

        # calculattion for gap
        pipe_length = int(
            (SCREEN_HEIGHT -  # fill window from top to bottom
             3 * Bird.HEIGHT -  # make room for bird to fit through
             3 * PipePair.PIECE_HEIGHT) /  # 2 end pieces + 1 body piece
            PipePair.PIECE_HEIGHT  # to get number of pipe pieces
        )

        # create random pipes and set upper and lower pipe length
        self.pipe_bl = randint(1, pipe_length)
        self.pipe_tp = pipe_length - self.pipe_bl

        # display lower pipe
        for i in range(1, self.pipe_bl + 1):
            piece_position = (0, SCREEN_HEIGHT - i * PipePair.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, piece_position)
        bottom_pipe_end_y = SCREEN_HEIGHT - self.bottom_pipe_height_pixel
        bottom_end_piece_position = (0, bottom_pipe_end_y - PipePair.PIECE_HEIGHT)
        self.image.blit(pipe_end_img, bottom_end_piece_position)

        # display upper pipe
        for i in range(self.pipe_tp):
            self.image.blit(pipe_body_img, (0, i * PipePair.PIECE_HEIGHT))
        top_pipe_end_y = self.top_pipe_height_pixel
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))

        # compensate for added end pieces
        self.pipe_tp += 1
        self.pipe_bl += 1

        # for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_pipe_height_pixel(self):
        return self.pipe_tp * PipePair.PIECE_HEIGHT

    @property
    def bottom_pipe_height_pixel(self):
        return self.pipe_bl * PipePair.PIECE_HEIGHT

    @property
    def rect(self):
        # Return pipe pair rectangle for collision detection
        return Rect(self.x, 0, PipePair.WIDTH, PipePair.PIECE_HEIGHT)

    def update(self, delta_frames=1):
        # update pipe pair
        self.x -= ANIMATION_SPEED * conversions.frames_to_msec(delta_frames)

    @property
    def visible(self):
        # display pipe?
        if -PipePair.WIDTH < self.x < SCREEN_WIDTH:
            return True

    def collides_with(self, bird):
        # detects collision
        return pygame.sprite.collide_mask(self, bird)


class conversions():
    def frames_to_msec(frames, fps=FPS):
        return 1000.0 * frames / fps

    def msec_to_frames(milliseconds, fps=FPS):
        return fps * milliseconds / 1000.0


def load_image(image):
    image = image + ".png"
    file_name = os.path.join('.', 'images', image)
    # print(file_name)
    img = pygame.image.load(file_name)
    img.convert()
    return img


def setup_environment():
    images = ['1', 'pipe_end', 'pipe_body', 'bird_wing_up', 'bird_wing_down']
    for item in images:
        load_image(item)


def main():
    # progarm enters here

    # set up game environment window
    pygame.init()
    backend_frame = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Flappy Bird')

    clock = pygame.time.Clock()
    score_style = pygame.font.SysFont(None, 28, bold=True)

    images = setup_environment()
    pipes_images = (load_image('pipe_end'), load_image('pipe_body'))

    # pygame.time.wait(1000000)
    wing_up = 'bird_wing_up'
    wing_down = 'bird_wing_down'

    bird = Bird(2, (load_image(wing_up), load_image(wing_down)))

    pipes = deque()

    frame_clock = 0  # this counter is only incremented if the game isn't paused
    score = 0
    done = False
    while not done:
        clock.tick(FPS)

        if not (frame_clock % conversions.msec_to_frames(PipePair.ADD_INTERVAL)):
          pipes.append(PipePair(pipes_images))

        for x in (0, SCREEN_WIDTH / 2):
            backend_frame.blit(load_image('background'), (x, 0))

        bird.update()
        backend_frame.blit(bird.animate, bird.rect)

        for p in pipes:
            p.update()
            backend_frame.blit(p.image, p.rect)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                done = True
                break
            elif event.type == MOUSEBUTTONUP or (event.type == KEYUP and
                                                 event.key in (K_UP, K_RETURN, K_SPACE)):
                bird.free_fall_time = Bird.CLIMB_DURATION

        # update and display score
        for p in pipes:
            if p.x + PipePair.WIDTH < bird.x and not p.score_count:
                score += 1
                p.score_count = True

        #score updation and siplay
        score_surface = score_style.render("Score: " + str(score), True, (255, 255, 255))
        score_x = SCREEN_WIDTH / 2 - score_surface.get_width() / 2
        backend_frame.blit(score_surface, (score_x, PipePair.PIECE_HEIGHT))

        #collision check
        pipe_collision = any(p.collides_with(bird) for p in pipes)
        if pipe_collision or 0 >= bird.y or bird.y >= SCREEN_HEIGHT - Bird.HEIGHT:
            done = True

        #updates surface
        pygame.display.flip()
        frame_clock += 1


    print('Game over! Score: %i' % score)
    pygame.quit()


main()