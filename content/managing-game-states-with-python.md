title: Managing game states with Python
date: 2020-06-28

In this article I'm going to explain how to manage game states in Python (and Pygame). By game
states I mean things like the main menu, the pause menu, the settings screen, the actual game, and
so on. I'm going to cover two methods that can be used, namely nested while loops and state
machines, and by the end of this article I hope that you'll see that state machines are probably
better.

### Initial model

The model I learnt when first learning game development with Pygame was this, called the game loop:

```
# load/create any data needed

running = True

while running:
	# handle events/user input

	# update and handle logic

	# render stuff to the screen
```

This is also known as the input-update-render loop, and you can find more information about it
[here](https://gameprogrammingpatterns.com/game-loop.html). This model is nice because it's simple
and so is easy to understand/develop on. However, it's also seriously flawed - it only understands
one state; if you have more than one state in your game then this model will need to be changed
quite significantly to work.

### Loops within loops

I think we can agree that the original model works quite well, so instead of completely rewriting
it we can adapt it to work with multiple states. We start with an overall `while` loop, which
holds most of the program. Within this main loop, we have seperate loops for each individual state,
with global variables to show which state the game is currently in and `if` statements to switch
between them. The code might look something like this:

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

This new code solves the problem of not being able to have new states, however it also creates
some new problems:

- Switching between states isn't an elegant process, as you need to destroy any
data that is no longer needed/will interfere with other states and create new data for use in the
new state on the fly, as soon as the end condition for a state is reached.

- Maintenance also becomes an issue, as you're repeating a lot of code all
over the place (handling the `pygame.QUIT` event and drawing things to the screen with
`pygame.display.flip()`), which can lead to errors in your code.

- Passing data between states can also become very complicated, as you'll need share global
variables between states in order to get them to share the data. This can also lead to a lot
of repeated code, which again is not good.

So, this isn't suitable. What about the state machine?

### The States class

Let's take a step back for a moment. Each state is essentially doing the same 4 things:

- Creating/destroying data when they start/stop
- Handling events and user input
- Updating the data that they have depending on the input
- Rendering things to the screen when the updates are completed

Exactly *how* they do this varies from state to state, but we know that they do the same things.
Let's create a class to demonstrate this:

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

This class provides the basis for all the other states.
