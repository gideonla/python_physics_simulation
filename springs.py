import random
from math import pi
import pygame
import PyParticle

(width, height) = (400, 400)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('gas simulation')

universe = PyParticle.Environment(width, height)
universe.colour = (0, 0, 0)
universe.colour = (0, 0, 0)
universe.addFunctions(['move', 'bounce', 'drag', 'accelerate'])
universe.acceleration = (pi, 0.001)
universe.mass_of_air = 0.00

def calculateRadius(mass):
    return 0.5 * mass ** (0.5)


for p in range(3):
    universe.addParticles(mass=100, size=16, speed=2, elasticity=0.8, colour=(20,40,200))

universe.addSpring(0,1, length=100, strength=0.05)
universe.addSpring(1,2, length=100, strength=0.01)
universe.addSpring(2,0, length=80, strength=0.05)

running = True
paused = False

selected_particle = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = (True,False)[False]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            selected_particle = universe.findParticle(*pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_particle = None
        if not paused:
            universe.update()
    screen.fill(universe.colour)

    for p in universe.particles:
        if selected_particle:
            selected_particle.mouseMove(*pygame.mouse.get_pos())
        pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, 0)
    for s in universe.springs:
        pygame.draw.aaline(screen, (255, 255, 255), (int(s.p1.x), int(s.p1.y)), (int(s.p2.x), int(s.p2.y)))

    universe.update()



    pygame.display.flip()
