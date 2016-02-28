import os
import shelve
import sys

# Available sizes
sizes = {'personal', 'small', 'medium', 'large'}
# Available pizza bases
bases = {'pan', 'homestyle', 'edge', 'stuffed', 'thin'}
# Available sauces
sauces = {'tomato', 'alfredo', 'beef-gravy', 'indian-butter', 'old-world-tomato'}
# Available cheeses
cheeses = {'regular', 'remove', 'light', 'extra'}

# Sides that toppings can be added to
sides = {'left', 'right', 'both'}

# List of available meat options
meats = ['pepperoni', 'bacon-crumble', 'bacon', 'ham', 'grilled-chicken-breast', 'italian-sausage', 'mild-sausage', 'beef', 'smokey-maple-bacon']
# List of available veggies options
veggies = ['mushroom', 'green-pepper', 'pineapple', 'red-onions', 'roasted-red-peppers', 'hot-peppers', 'tomatoes', 'marinated-tomatoes', 'black-olives', 'roasted-garlic', 'parmesan', 'cheddar-cheese', 'cheese-curds', 'feta-cheese', 'pesto']

# Pizza object
class Pizza(object):

    # Declares default pizza options
    def __init__(self):
        self.meats = {'left': set(), 'right': set()}
        self.veggies = {'left': set(), 'right': set()}
        self.cheese = {'left': 'regular', 'right': 'regular'}
        self.size = 'personal'
        self.base = 'pan'
        self.sauce = 'tomato'

    def change_size(self, size):
        # Check if the size is valid and if so, update the pizza
        if size not in sizes:
            return False
        self.size = size
        return True

    def change_base(self, base):
        # Check if the base is valid and if so, update the pizza
        if base not in bases:
            return False
        self.base = base
        return True

    def change_sauce(self, sauce):
        # Check if the sauce type is valid and if so, update the pizza
        if sauce not in sauces:
            return False
        self.sauce = sauce
        return True

    def change_cheese(self, side_arg, cheese):
        # If the side is not 'left', 'right', or 'both', return False
        if side_arg not in sides:
            return False

        # Create a list of the sides the cheese is being changed on
        if side_arg == 'both':
            side_arg = sides
        else:
            side_arg = [side]

        # Make sure the cheese is a valid type
        if cheese not in cheeses:
            return False

        # Update the cheese
        for side in side_arg:
            self.cheese[side] = cheese
        return True


    def add_topping(self, side_arg, topping):
        # If the side is not 'left', 'right', or 'both', return False
        if side_arg not in sides:
            return False

        # Create a list of the sides the topping is being added to
        if side_arg == 'both':
            side_arg = sides
        else:
            side_arg = [side_arg]

        # Find the index of the topping in the meat or veggies list, or return False if it isn't found
        topping_list = None
        if topping in meats:
            topping_list = self.meats
        elif topping in veggies:
            topping_list = self.veggies
        else:
            return False

        # Adding the topping to the specified sides
        for side in side_arg:
            topping_list[side].add(topping)

        return True

    def remove_topping(self, side_arg, topping):
        # If the side is not 'left' or 'right', return False
        if side_arg not in sides:
            return False

        # Create a list of the sides the topping is being added to
        if side_arg == 'both':
            side_arg = sides
        else:
            side_arg = [side]

        if topping not in meats and topping not in veggies:
            return False

        # Adding the topping to the specified sides
        for side in side_arg:
            self.meats[side].discard(topping)
            self.veggies[side].discard(topping)
        return True

    def get_status(self):
        # Compile a string containing the left meats
        if len(self.meats['left']) == 0:
            left_meats = "\tNone"
        else:
            first_meat = self.meats['left'].pop()
            left_meats = "\t{0}".format(first_meat)
            for meat in self.meats['left']:
                left_meats += "\n\t\t\t{0}".format(meat)
            self.meats['left'].add(first_meat)

        # Compile a string containing the left veggies
        if len(self.veggies['left']) == 0:
            left_veggies = "\tNone"
        else:
            first_veggie = self.veggies['left'].pop()
            left_veggies = "\t{0}".format(first_veggie)
            for veggie in self.veggies['left']:
                left_veggies += "\n\t\t\t{0}".format(veggie)
            self.veggies['left'].add(first_veggie)

        # Compile a string containing the right meats
        if len(self.meats['right']) == 0:
            right_meats = "\tNone"
        else:
            first_meat = self.meats['right'].pop()
            right_meats = "\t{0}".format(first_meat)
            for meat in self.meats['right']:
                right_meats += "\n\t\t\t{0}".format(meat)
            self.meats['right'].add(first_meat)

        # Compile a string containing the right veggies
        if len(self.veggies['right']) == 0:
            right_veggies = "\tNone"
        else:
            first_veggie = self.veggies['right'].pop()
            right_veggies = "\t{0}".format(first_veggie)
            for veggie in self.veggies['right']:
                right_veggies += "\n\t\t\t{0}".format(veggie)
            self.veggies['right'].add(first_veggie)

        properties = (
            "\n\tYour pizza so far:\n"
            "\t------------------------------\n"
            "\tSize:\t\t{0}\n"
            "\tBase:\t\t{1}\n"
            "\tSauce:\t\t{2}\n"
            "\t------------------------------\n"
            "\tLeft cheese:\t{3}\n"
            "\tLeft Meats:"
            "{4}\n"
            "\tLeft Veggies:"
            "{5}\n"
            "\t------------------------------\n"
            "\tRight cheese:\t{6}\n"
            "\tRight Meats:"
            "{7}\n"
            "\tRight Veggies:"
            "{8}\n"
        )

        properties = properties.format(
            self.size,
            self.base,
            self.sauce,
            self.cheese['left'],
            left_meats,
            left_veggies,
            self.cheese['right'],
            right_meats,
            right_veggies)

        return properties

# Prints a sick ass pizza
def print_pizza():
    print("""
        _....._
    _.:`.--|--.`:._
  .: .'\o  | o /'. '.
 // '.  \ o|  /  o '.\\
//'._o'. \ |o/ o_.-'o\\\\
|| o '-.'.\|/.-' o   ||
||--o--o-->|<o-----o-||
\\\\  o _.-'/|\\'-._o  o//
 \\\\.-'  o/ |o\ o '-.//
  '.'.o / o|  \ o.'.'
    `-:/.__|__o\:-'
       `"--=--"`
    """)

def add_new_pizza(branch):
    global last_branch_added

    if branch in pizzas and branch != last_branch_added:
        print('You are attempting to create a new branch but a pizza already exists.')
        print(pizzas[branch].get_status())
        print('Run this command again to override your pizza.')
        last_branch_added = branch
        return False

    last_branch_added = None
    pizzas[branch] = Pizza()
    print('Initialized basic pizza.')
    print('Switching to branch {0}.'.format(branch))
    print(pizzas[branch].get_status())

pizzas = {}
last_branch_added = None

# Reset all variables to their default value
# If the globals above are updated, they should be updated here
def set_defaults():
    global pizzas
    global last_branch_added

    pizzas = {}
    last_branch_added = None

def print_welcome_message():
    print_pizza()
    print('Welcome to git-pizza.')
    print('To get started, create a new order with \'gitpizza init\'\n')

# Defining folder for persistence between runs
shelve_folder = 'shelves'
shelve_name = 'pizza-persistence'
shelve_fullname = os.path.join(shelve_folder, shelve_name)

# Create the folder for persistence if it doesn't exist
if not os.path.exists(shelve_folder):
    os.makedirs(shelve_folder)

# Load the persistence if it exists
if os.path.isfile(shelve_fullname):
    with shelve.open(shelve_fullname, 'r') as shelf:
        pizzas = shelf['pizzas']
        last_branch_added = shelf['last_branch_added']

# Argument parsing
def parse_single_arg(arg):
    global pizzas
    if 'init' == arg:
        if len(pizzas) == 0:
            pizzas = {}
            add_new_pizza('master')
        else:
            print('You have already initiated an order.')
            print('You\'ll have to delete your current pizzas to create a new order.')
            print('Try the command \'gitpizza branch\' to see your current pizzas.')
    elif 'branch' == arg:
        if (len(pizzas)) == 0:
            print('You haven\'t created any pizzas. Try running \'gitpizza init\'')
        else:
            print('x')
    elif 'reset' == arg:
        set_defaults()
        print('Your order has been reset.')

if len(sys.argv) <= 1:
    print_welcome_message()
elif len(sys.argv) == 2:
    if len(pizzas) == 0 and 'init' != sys.argv[1]:
        print_welcome_message()
    else:
        parse_single_arg(sys.argv[1])

# Save the configuration for the next run
with shelve.open(shelve_fullname, 'c') as shelf:
    shelf['pizzas'] = pizzas
    shelf['last_branch_added'] = last_branch_added