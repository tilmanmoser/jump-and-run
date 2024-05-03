import pygame

INITIAL_DISPLAY_SIZE = [800, 500]
FPS = 60


class Editor:
    def __init__(self):
        # display
        pygame.init()
        pygame.display.set_caption("Level Editor")
        self.screen = pygame.display.set_mode(INITIAL_DISPLAY_SIZE, pygame.RESIZABLE)
        self.display = pygame.Surface(INITIAL_DISPLAY_SIZE)
        self.display_scale = 1

        # loop
        self.clock = pygame.Clock()

        # inputs
        self.movement = [False, False, False, False]
        self.shift = False
        self.click = [False, False]

    def resize(self, size):
        # fixed height, variable width
        self.display_scale = INITIAL_DISPLAY_SIZE[1] / size[1]
        self.display = pygame.Surface((size[0] * self.display_scale, INITIAL_DISPLAY_SIZE[1]))

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass

    def update(self):
        pass

    def render(self):
        # display
        self.display.fill((0, 0, 0, 0))

        # screen
        self.screen.fill((0, 0, 0, 0))
        self.screen.blit(
            pygame.transform.scale(self.display, (self.display.get_width() / self.display_scale, self.display.get_height() / self.display_scale)), (0, 0)
        )
        pygame.display.update()

    def run(self):
        running = True
        while running:

            # user inputs
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.VIDEORESIZE:
                    self.resize(event.dict["size"])
                if event.type == pygame.VIDEOEXPOSE:
                    self.resize(self.screen.get_size())
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = True
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = True
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.movement[2] = True
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.movement[3] = True
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.movement[0] = False
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.movement[1] = False
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.movement[2] = False
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self.movement[3] = False
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                        self.shift = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click[0] = True
                    if event.button == 3:
                        self.click[1] = True
                    if event.button == 4:
                        self.scroll_up()
                    if event.button == 5:
                        self.scroll_down()
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.click[0] = False
                    if event.button == 3:
                        self.click[1] = False

            self.update()
            self.render()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Editor().run()
