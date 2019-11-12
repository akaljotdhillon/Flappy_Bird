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
            self.y -= (Bird.CLIMB_SPEED * frames_to_msec(delta_frames) *
                       (1 - math.cos(frac_climb_done * math.pi)))

            self.free_fall_time -= frames_to_msec(delta_frames)
        else:
            self.y += Bird.SINK_SPEED * frames_to_msec(delta_frames)

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


class PipePair(pygame.sprite.Sprite):
    """Represents an obstacle.

    A PipePair has a top and a bottom pipe, and only between them can
    the bird pass -- if it collides with either part, the game is over.

    Attributes:
    x: The PipePair's X position.  This is a float, to make movement
        smoother.  Note that there is no y attribute, as it will only
        ever be 0.
    image: A pygame.Surface which can be blitted to the display surface
        to display the PipePair.
    mask: A bitmask which excludes all pixels in self.image with a
        transparency greater than 127.  This can be used for collision
        detection.
    pipe_tp: The number of pieces, including the end piece, in the
        top pipe.
    pipe_bl: The number of pieces, including the end piece, in
        the bottom pipe.

    Constants:
    WIDTH: The width, in pixels, of a pipe piece.  Because a pipe is
        only one piece wide, this is also the width of a PipePair's
        image.
    PIECE_HEIGHT: The height, in pixels, of a pipe piece.
    ADD_INTERVAL: The interval, in milliseconds, in between adding new
        pipes.
    """

    WIDTH = 80
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 3500

    def __init__(self, pipes_images):

        # print(pipes_images)
        pipe_end_img, pipe_body_img = pipes_images
        self.x = float(SCREEN_WIDTH - 1)
        self.score_count = False

        self.image = pygame.Surface((PipePair.WIDTH, SCREEN_HEIGHT), SRCALPHA)

        # calculate
        pipe_length = int(
            (SCREEN_HEIGHT -  # fill window from top to bottom
             3 * Bird.HEIGHT -  # make room for bird to fit through
             3 * PipePair.PIECE_HEIGHT) /  # 2 end pieces + 1 body piece
            PipePair.PIECE_HEIGHT  # to get number of pipe pieces
        )

        # create random pipes
        self.pipe_bl = randint(1, pipe_length)
        self.pipe_tp = pipe_length - self.pipe_bl

        # display lower pipe
        for i in range(1, self.pipe_bl + 1):
            piece_position = (0, SCREEN_HEIGHT - i * PipePair.PIECE_HEIGHT)
            self.image.blit(pipe_body_img, piece_position)
        bottom_pipe_end_y = SCREEN_HEIGHT - self.bottom_height_pixel
        bottom_end_piece_position = (0, bottom_pipe_end_y - PipePair.PIECE_HEIGHT)
        self.image.blit(pipe_end_img, bottom_end_piece_position)

        # display upper pipe
        for i in range(self.pipe_tp):
            self.image.blit(pipe_body_img, (0, i * PipePair.PIECE_HEIGHT))
        top_pipe_end_y = self.top_height_pixel
        self.image.blit(pipe_end_img, (0, top_pipe_end_y))

        # compensate for added end pieces
        self.pipe_tp += 1
        self.pipe_bl += 1

        # for collision detection
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_height_pixel(self):
        """Get the top pipe's height, in pixels."""
        return self.pipe_tp * PipePair.PIECE_HEIGHT

    @property
    def bottom_height_pixel(self):
        """Get the bottom pipe's height, in pixels."""
        return self.pipe_bl * PipePair.PIECE_HEIGHT

    @property
    def visible(self):
        """Get whether this PipePair on screen, visible to the player."""
        return -PipePair.WIDTH < self.x < SCREEN_WIDTH

    @property
    def rect(self):
        """Get the Rect which contains this PipePair."""
        return Rect(self.x, 0, PipePair.WIDTH, PipePair.PIECE_HEIGHT)

    def update(self, delta_frames=1):
        """Update the PipePair's position.

        Arguments:
        delta_frames: The number of frames elapsed since this method was
            last called.
        """
        self.x -= ANIMATION_SPEED * frames_to_msec(delta_frames)

    def collides_with(self, bird):
        """Get whether the bird collides with a pipe in this PipePair.

        Arguments:
        bird: The Bird which should be tested for collision with this
            PipePair.
        """
        return pygame.sprite.collide_mask(self, bird)


def frames_to_msec(frames, fps=FPS):
    """Convert frames to milliseconds at the specified framerate.

    Arguments:
    frames: How many frames to convert to milliseconds.
    fps: The framerate to use for conversion.  Default: FPS.
    """
    return 1000.0 * frames / fps


def msec_to_frames(milliseconds, fps=FPS):
    """Convert milliseconds to frames at the specified framerate.

    Arguments:
    milliseconds: How many milliseconds to convert to frames.
    fps: The framerate to use for conversion.  Default: FPS.
    """
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
    done = paused = False

    while not done:
        clock.tick(FPS)

        # Handle this 'manually'.  If we used pygame.time.set_timer(),
        # pipe addition would be messed up when paused.
        if not (paused or frame_clock % msec_to_frames(PipePair.ADD_INTERVAL)):
            pp = PipePair(pipes_images)
            pipes.append(pp)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
                paused = not paused
            elif e.type == MOUSEBUTTONUP or (e.type == KEYUP and
                                             e.key in (K_UP, K_RETURN, K_SPACE)):
                bird.free_fall_time = Bird.CLIMB_DURATION

        if paused:
            continue  # don't draw anything

        # check for collisions
        pipe_collision = any(p.collides_with(bird) for p in pipes)
        if pipe_collision or 0 >= bird.y or bird.y >= SCREEN_HEIGHT - Bird.HEIGHT:
            done = True

        for x in (0, SCREEN_WIDTH / 2):
            backend_frame.blit(load_image('background'), (x, 0))

        while pipes and not pipes[0].visible:
            pipes.popleft()

        for p in pipes:
            p.update()
            backend_frame.blit(p.image, p.rect)

        bird.update()
        backend_frame.blit(bird.animate, bird.rect)

        # update and display score
        for p in pipes:
            if p.x + PipePair.WIDTH < bird.x and not p.score_count:
                score += 1
                p.score_count = True

        score_surface = score_style.render("Score: " + str(score), True, (255, 255, 255))
        score_x = SCREEN_WIDTH / 2 - score_surface.get_width() / 2
        backend_frame.blit(score_surface, (score_x, PipePair.PIECE_HEIGHT))

        pygame.display.flip()
        frame_clock += 1
    print('Game over! Score: %i' % score)
    pygame.quit()


main()