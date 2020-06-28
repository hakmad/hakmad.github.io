title: Managing game states with Python
date: 2020-06-28

When first learning game development with Python/Pygame, I was taught this model:

This model is nice for several reasons, perhaps the most important one being that it is *simple*.
No need for complicated structures and messy code: this will do the job and do it well. An example
of it in use is shown here:

```
import pygame

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((640, 480))

running = True
while running:
	clock.tick(30)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	
	screen.fill((255, 255, 255))

	pygame.display.flip()

pygame.quit()

```

Admittedly, this code doesn't do all that much, it just shows a white screen. The point is that
this model makes it very easy to go from flowcharts and pseudocode to actual code; you can see the
different stages of the model in the code above. This model can also be applied to much bigger
programs that actually run games, such as [this](https://raw.githubusercontent.com/kidscancode/
pygame_tutorials/master/shmup/shmup.py). There is a serious problem though.

When using this model, you assume that there is only one state in the game. 
