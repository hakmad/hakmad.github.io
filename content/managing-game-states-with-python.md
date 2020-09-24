title: Managing game states with Python
date: 2020-09-24

In this article I'm going to explain how to manage game states in Python (and
Pygame). By game states I mean things like the main menu, the pause menu, the
settings screen, the actual game, and so on. I'm going to cover two methods
that can be used, namely nested while loops and state machines, and by the
end of this article I hope that you'll see that state machines are probably
better.

### Initial model

The model I learnt when first learning game development with Pygame was this,
called the game loop:

```
# load/create any data needed

running = True

while running:
	# handle events/user input

	# update and handle logic

	# render stuff to the screen
```

This is also known as the input-update-render loop, and you can find out more
about it [here](https://gameprogrammingpatterns.com/game-loop.html). This
model is nice because it's simple and so is easy to understand/develop on.
However, it's also seriously flawed - it only understands one state; if you
have more than one state in your game then this model will need to be changed
quite significantly to work.

### Loops within loops

I think we can agree that the original model works quite well, so instead of
completely rewriting it we can adapt it to work with multiple states. We start
with an overall `while` loop, which holds most of the program. Within this
main loop, we have seperate loops for each individual state, with global
variables to show which state the game is currently in and `if` statements
to switch between them. The code might look something like this:

```
# load/create any data needed

running = True
current_state = "start"

while running:
	if current_state == "start":
		while current_state == "start":
			# handle events/user input for start state
			
			# update and handle logic for start state

			# render stuff to the screen for start state

	if current_state == "game":
		while current_state == "game":
			# handle events/user input for game state

			# update and handle logic for game state

			# render stuff to the screen for game state
```

This new code solves the problem of not being able to have new states, however
it also creates some new problems:

- Switching between states isn't an elegant process, as you need to destroy
any data that is no longer needed/will interfere with other states and create
new data for use in the new state on the fly, as soon as the end condition for
a state is reached.

- Maintenance also becomes an issue, as you're repeating a lot of code all
over the place (handling the `pygame.QUIT` event and drawing things to the
screen with `pygame.display.flip()`), which can lead to errors in your code.

- Passing data between states can also become very complicated, as you'll
need share global variables between states in order to get them to share the
data. This can also lead to a lot of repeated code, which again is not good.

So, this isn't suitable. What about the state machine?

### The States and Control class

Let's take a step back for a moment. Each state is essentially doing the same
4 things:

- Creating/destroying data when they start/stop
- Handling events and user input
- Updating the data that they have depending on the input
- Rendering things to the screen when the updates are completed

Exactly *how* they do this varies from state to state, but we know that they
do the same things. Let's create a class to demonstrate this:

```
class States:
	def __init__(self):
		self.running = True
		self.next = None

	def setup(self):
		pass
		
	def cleanup(self):
		pass

	def handle_events(self, event):
		pass

	def update(self):
		pass

	def render(self, screen):
		pass
```

This class provides the basis for all the other states. All the methods
defined here are going to be overwritten, but we still need to make it clear
that these methods are needed, so we write them in anyway. Let's define
another class, `Control`:

```
class Control:
	def __init__(self, state_dict, start_state):
		self.screen = pygame.display.set_mode((width, height))
		self.clock = pygame.time.Clock()
		self.running = True
		self.state_dict = state_dict
		self.current_state = self.state_dict[start_state]
		self.current_state.setup()
		self.main_loop()

	def handle_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			self.current_state.handle_events(event)

		if not(self.current_state.running):
			self.change_state()
	
	def change_state(self):
		next_state = self.current_state.next
		self.current_state.cleanup()
		self.current_state = self.state_dict[next_state]
		self.current_state.setup()

	def main_loop(self):
		while self.running:
			self.clock.tick(fps)
			self.handle_events()
			self.current_state.update()
			self.current_state.render(self.screen)
			pygame.display.flip()
```

That's a lot of code going on at once! Let's break it down method by method:

- `__init__`: this is the method that is executed when we create a new
`Control` object. It takes 2 arguments: `state_dict` (a dictionary containing
`State` objects with relevant names) and `start_state` (a string representing
the first state in `state_dictionary` that should be run). It sets up some
basic variables needed for Pygame to run (`screen`, `clock` and `running`) and
then moves onto initialising the first state and running the `main_loop`
method.

- `main_loop`: this is where the majority of our program will be spent. If you
look at the code you can see that it is, in essence, just a game loop.

- `handle_events`: this method is used to handle any events. The `pygame.QUIT`
event (the user closed the program) is handled by the `Control` class; all
other events are passed to the current state for it to deal with. The only
other event that the `Control` class manages is if the currently running
state stops, in which case it runs the `change_state` method.

- `change_state`: this method is used to switch between states. It cleans up
the currently running state by using that states method, then overwrites
the `current_state` with a state from `states_dict`. This new state is
specified by the `next_state` attribute in the `State` class. It then sets
up the new state, and the process of switching states is complete.

The idea here is that we create several states (using the `States` class),
and then create a control object (from the `Control` class) to run our game.
The control object runs each state forever until either the program is
stopped or the states `running` attribute is set to `False`. When the latter
happens, the control object looks for the next state in the dictionary and
cleans up the old state before setting up the new one.

### Practical use

Let's make some actual states to demonstrate how to use this. It won't be
particularly pretty or useful, but it will hopefully be good enough to show
how to build your own games using this method. Before we start, here is some
boilerplate code to get us started:

```
import pygame

width = 640
height = 480
fps = 60

class Square(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, height // 2)

    def update(self):
        self.rect.x += 5
        if self.rect.left > width:
            self.rect.right = 0
```

All we do here is import pygame and set the `width`, `height` and `fps`
variables, as well as create a `Square` class (which we will use later).

Let's create the different states now:

```
class Menu(States):
    def __init__(self):
        self.next = "game"

    def setup(self):
        self.running = True

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.running = False

    def render(self, screen):
        screen.fill((0, 0, 255))

class Game(States):
    def __init__(self):
        States.__init__(self)
        self.next = "menu"

    def setup(self):
        self.running = True
        self.square = Square()
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.square)

    def cleanup(self):
        del self.square
        del self.sprites

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.running = False

    def update(self):
        self.sprites.update()

    def render(self, screen):
        screen.fill((0, 255, 0))
        self.sprites.draw(screen)
```

The first class, `Menu`, is for the menu state. Not much actually happens in
this state; it renders the screen blue and when the space bar is pressed the
state ends. The second class, `Game`, is for the game state. This state
creates 2 attributes: `square` (using the `Square` class defined earlier) and
`sprites` (a `pygame.sprite.Group` object, used for rendering and updating
groups of `pygame.sprite.Sprite` objects - though in this case we only have
one). It continually updates and renders the square to the screen, and again
only stops when the space bar is pressed. When the `Menu` state ends, the
program switches to the `Game` state, and vice versa.

Finally, let's actually use the `Control` class that we defined earlier:

```
states = {
	"menu": Menu(),
	"game": Game(),
	}

control = Control(states, "menu")

pygame.quit()
```

We first create a dictionary containing all the different states that will be
in the program: in ours we have the `Game` and `Menu` states. Note that the
key for the `Menu` state is the same as `Game.next` - the reason for this is
because when the `Game` state ends, the program will look at `Game.next` for
the next state to run and will use the value it gets in the dictionary. We
then create a `Control` object. This takes the `states` dictionary we created
and also a string (in this case, `"menu"`) as arguments, and starts the game.
The game keeps running in the manner described above - recieving input,
updating based on the input (plus any other factors) and rendering to the
screen, as well as changing states as need be. When the user decides they've
had enough of the red square floating across a green screen, they quit the
program, at which point the `pygame.quit` function is called and the program
ends. A few images of the game can be seen
[here](https://imgur.com/a/qZlGCEU).

### Review

Let's review what we've done. We've created 2 important classes:

- The `States` class
- The `Control` class

We use the `States` class to create different states that will be used by the
program, and use the `Control` class to manage and switch between the
different states. The other classes (`Menu` and `Game`) aren't important as
they are specific to this example. So obviously, we have solved the problem
of having multiple states, but have we solved the other problems by switching
to this model?

I'd say so. The process of switching states becomes much more elegant here, as
states are given a chance to clean up themselves before the next state starts
and sets up it's data. Maintenance is somewhat easier, as each state has it's
own seperate class. Passing data between states still relies on using global
variables (even more so, given that we are now using classes), however it is
definitely possible to share data using a dictionary:

```
class States:
	share = {}
	def __init__(self):
		self.running = True
		self.next = None
```

Now, if a state wanted to share or access some data that was shared, they
can use the `share` dictionary that is part of their class.

We've solved all the major problems. The next question becomes is this even
worth the effort? It isn't world breaking if I choose to use the loops within
loops model, why should I bother with all this? It really depends on the size
and structure of your project, but in my opinion I think it is worth it.
Having a clear architecture to your program means that should you expand it
later on, you have the scaffolding already in place to make your life easier.

One more thing before I conclude - the way I have implemented this is by no
means perfect, in fact I can already spot several flaws but I am too lazy to
go back and fix them. The point of this article was to simply demonstrate how
to go about doing this, as well as the idea and concepts behind a state
machine. How you choose to do this is entirely up to you: you could choose to
change the methods of how the `Control` class sets up its data, you could add
extra features to the different classes, you could even get rid of the
`Control` class entirely and just stick with a normal program to handle the
different states. The world really is your oyster here.

### Further reading

If you're more interested in the theory about state machines and what they
can do, I'd suggest reading [this article from Game Programming
Patterns](https://gameprogrammingpatterns.com/state.html) (which also contains
a lot of other useful and interesting programming patterns that don't just
apply to games) and [this
article from Source Making](https://sourcemaking.com/design_patterns/state).
If you're more interested in implementing this in Python, then [this forum
post](https://python-forum.io/Thread-PyGame-Creating-a-state-machine), [this
reddit post](https://www.reddit.com/r/pygame/comments/3kghhj) and [this GitHub
repo](https://github.com/Mekire/pygame-mutiscene-template-with-movie) should
be of interest to you.

I hope you enjoyed and/or learnt something from the article, if you have any
problems or suggestions please feel free to make an issue on GitHub
[here](https://github.com/hakmad/hakmad.github.io/issues). I'm not
particularly good at writing long articles like this, so all advice is
welcome!
