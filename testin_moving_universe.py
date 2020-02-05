import pygame

from PyParticle import *


class UniverseScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        (self.dx, self.dy) = (0, 0)
        (self.mx, self.my) = (0, 0)
        self.magnification = 1.0

    def scroll(self, dx=0, dy=0):
        self.dx += dx * width / (self.magnification * 10)
        self.dy += dy * height / (self.magnification * 10)

    def zoom(self, zoom):
        self.magnification *= zoom
        self.mx = (1 - self.magnification) * self.width / 2
        self.my = (1 - self.magnification) * self.height / 2

    def reset(self):
        (self.dx, self.dy) = (0, 0)
        (self.mx, self.my) = (0, 0)
        self.magnification = 1.0


(width, height) = (400, 400)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('gas simulation')

universe = Environment(width, height)
universe.colour = (0, 0, 0)
universe.addFunctions(['move', 'attract', 'combine'])
universe_screen = UniverseScreen(width, height)


def calculateRadius(mass):
    return 0.5 * mass ** (0.5)


key_move_map = {
    pygame.K_LEFT: lambda x: x.scroll(dx=1),
    pygame.K_RIGHT: lambda x: x.scroll(dx=-1),
    pygame.K_UP: lambda x: x.scroll(dy=-1),
    pygame.K_DOWN: lambda x: x.scroll(dy=1),
    pygame.K_EQUALS: lambda x: x.zoom(2),
    pygame.K_MINUS: lambda x: x.zoom(0.5),
    pygame.K_r: lambda x: x.reset()
}

for p in range(100):
    particle_mass = random.randint(1, 4)
    particle_size = calculateRadius(particle_mass)
    universe.addParticles(mass=particle_mass, size=particle_size, speed=0, colour=(255, 255, 255))

running = True
paused = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key in key_move_map:
                key_move_map[event.key](universe_screen)
            elif event.key == pygame.K_SPACE:
                paused = not paused
        if event.type == pygame.QUIT:
            running = False
    if not paused:
        universe.update()
    screen.fill(universe.colour)

    particles_to_remove = []
    for p in universe.particles:
        if 'collide_with' in p.__dict__:
            particles_to_remove.append(p.collide_with)
            p.size = calculateRadius(p.mass)
            del p.__dict__['collide_with']
        mag = universe_screen.magnification
        x = int(universe_screen.mx + (universe_screen.dx + p.x) * mag)
        y = int(universe_screen.my + (universe_screen.dy + p.y) * mag)
        size = int(p.size * mag)

        if p.size < 2:
            pygame.draw.rect(screen, p.colour, (x, y, 2, 2))
        else:
            pygame.draw.circle(screen, p.colour, (x, y), int(size), 0)

    for p in particles_to_remove:
        universe.particles.remove(p)

    pygame.display.flip()
