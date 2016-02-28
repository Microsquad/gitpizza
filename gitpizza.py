import os
import re
import shelve
import sys

class bcolors:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

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
        self.old_meats = None
        self.old_veggies = None

    def clear_merge_cache(self):
        self.old_meats = None
        self.old_veggies = None

    def change_size(self, size):
        self.clear_merge_cache()
        # Check if the size is valid and if so, update the pizza
        if size not in sizes:
            return False
        self.size = size
        return True

    def change_base(self, base):
        self.clear_merge_cache()
        # Check if the base is valid and if so, update the pizza
        if base not in bases:
            return False
        self.base = base
        return True

    def change_sauce(self, sauce):
        self.clear_merge_cache()
        # Check if the sauce type is valid and if so, update the pizza
        if sauce not in sauces:
            return False
        self.sauce = sauce
        return True

    def change_cheese(self, side_arg, cheese):
        self.clear_merge_cache()
        # If the side is not 'left', 'right', or 'both', return False
        if side_arg not in sides:
            return False

        # Create a list of the sides the cheese is being changed on
        if side_arg == 'both':
            side_arg = ['left', 'right']
        else:
            side_arg = [side_arg]

        # Make sure the cheese is a valid type
        if cheese not in cheeses:
            return False

        # Update the cheese
        for side in side_arg:
            self.cheese[side] = cheese
        return True

    def merge(self):
        meat_merged = False
        veggies_merged = False

        self.old_meats = {'left': self.meats['left'].copy(), 'right': self.meats['right'].copy()}
        self.old_veggies = {'left': self.veggies['left'].copy(), 'right': self.veggies['right'].copy()}

        if len(self.meats['left'] ^ self.meats['right']) > 0:
            meat_merged = True
            self.meats['left'] |= self.meats['right']
            self.meats['right'] |= self.meats['left']
        if len(self.veggies['left'] ^ self.veggies['right']) > 0:
            veggies_merged = True
            self.veggies['left'] |= self.veggies['right']
            self.veggies['right'] |= self.veggies['left']

        if not meat_merged and not veggies_merged:
            print('no changes added to commit (use ' + bcolors.BOLD + '\'gitpizza add\'' + bcolors.END + ')')
        else:
            if meat_merged:
                print(bcolors.GREEN + 'meat automerge success.' + bcolors.END)
            if veggies_merged:
                print(bcolors.GREEN + 'veggies automerge success.' + bcolors.END)
            print('use ' + bcolors.BOLD + '\'gitpizza revert\'' + bcolors.END + ' to undo.')

    def unmerge(self):
        if not self.old_meats or not self.old_veggies:
            print(bcolors.RED + 'fatal:' + bcolors.END + ' commands have been executed since the merge, reverting merge is not possible.')
        else:
            self.meats = self.old_meats
            self.veggies = self.old_veggies
            print('meat and veggie merge ' + bcolors.BOLD + 'reverted' + bcolors.END + '.')

    def add_topping(self, side_arg, topping):
        self.clear_merge_cache()
        # If the side is not 'left', 'right', or 'both', return False
        if side_arg not in sides:
            return False

        # Create a list of the sides the topping is being added to
        if side_arg == 'both':
            side_arg = ['left', 'right']
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
        self.clear_merge_cache()
        # If the side is not 'left' or 'right', return False
        if side_arg not in sides:
            return False

        # Create a list of the sides the topping is being added to
        if side_arg == 'both':
            side_arg = ['left', 'right']
        else:
            side_arg = [side_arg]

        if topping not in meats and topping not in veggies:
            return False

        # Adding the topping to the specified sides
        for side in side_arg:
            self.meats[side].discard(topping)
            self.veggies[side].discard(topping)
        return True

    def get_diff(self):
        if self.cheese['left'] != self.cheese['right']:
            cheese_diff = '\t{:<33}| {}'.format(bcolors.GREEN + self.cheese['left'] + bcolors.END, bcolors.RED + self.cheese['right'] + bcolors.END)
        else:
            cheese_diff = '\t{:<33}| {}'.format(self.cheese['left'], self.cheese['right'])

        left_meat = sorted(list(self.meats['left']))
        right_meat = sorted(list(self.meats['right']))

        meat_diff = ""
        i = 0
        if len(left_meat) == 0 and len(right_meat) == 0:
            meat_diff = '\t{0:<24}| {0}\n'.format('None')
        else:
            while i < len(left_meat):
                if left_meat[i] in right_meat:
                    meat_diff += '\t{0:<24}| {0}\n'.format(left_meat[i])
                    right_meat.remove(left_meat[i])
                    left_meat.remove(left_meat[i])
                    i -= 1
                i += 1
            for i in range(max(len(left_meat), len(right_meat))):
                left = ""
                right = ""
                if i < len(left_meat):
                    left = left_meat[i]
                if i < len(right_meat):
                    right = right_meat[i]
                meat_diff += '\t{:<33}| {}\n'.format(bcolors.GREEN + left + bcolors.END, bcolors.RED + right + bcolors.END)

        left_veggies = sorted(list(self.veggies['left']))
        right_veggies = sorted(list(self.veggies['right']))

        veggie_diff = ""
        i = 0
        if len(left_veggies) == 0 and len(right_veggies) == 0:
            veggie_diff = '\t{0:<24}| {0}\n'.format('None')
        else:
            while i < len(left_veggies):
                if left_veggies[i] in right_veggies:
                    veggie_diff += '\t{0:<24}| {0}\n'.format(left_veggies[i])
                    right_veggies.remove(left_veggies[i])
                    left_veggies.remove(left_veggies[i])
                    i -= 1
                i += 1
            for i in range(max(len(left_veggies), len(right_veggies))):
                left = ""
                right = ""
                if i < len(left_veggies):
                    left = left_veggies[i]
                if i < len(right_veggies):
                    right = right_veggies[i]
                veggie_diff += '\t{:<33}| {}\n'.format(bcolors.GREEN + left + bcolors.END, bcolors.RED + right + bcolors.END)

        diff = (
            "\n\tYour pizza so far:\n"
            "\n"
            "" + bcolors.BOLD + "\tLeft cheese\t\t| Right cheese\n" + bcolors.END + ""
            "\t{:-^50}\n"
            "{}\n"
            "\n"
            "" + bcolors.BOLD + "\tLeft meats\t\t| Right meats\n" + bcolors.END + ""
            "\t{:-^50}\n"
            "{}"
            "\n"
            "" + bcolors.BOLD + "\tLeft veggies\t\t|Right veggies\n" + bcolors.END + ""
            "\t{:-^50}\n"
            "{}\n"
        )

        diff = diff.format(
            '',
            cheese_diff,
            '',
            meat_diff,
            '',
            veggie_diff
        )

        return diff

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

def print_welcome_message():
    print_pizza()
    print('Welcome to gitpizza.')
    print('To get started, create a new order with \'gitpizza init\'\n')

def add_new_pizza(branch):
    global last_branch_added
    global current_branch

    if branch in pizzas and branch != last_branch_added:
        print('You are attempting to create a new branch but a pizza already exists.')
        print(pizzas[branch].get_status())
        print('Run this command again to override your pizza.')
        last_branch_added = branch
        return False

    last_branch_added = None
    pizzas[branch] = Pizza()
    order_info[branch] = order_info_global.copy()
    current_branch = branch
    print('Initialized basic pizza.')
    print('Switching to branch {0}.'.format(branch))
    print(pizzas[branch].get_status())

def switch_to_branch(branch):
    global current_branch

    if branch in pizzas:
        current_branch = branch
        print('Switching to branch {0}.'.format(branch))
        print(pizzas[branch].get_status())
    else:
        print(bcolors.RED + 'The branch ' + bcolors.END + bcolors.BOLD + branch + bcolors.END + bcolors.RED + ' does not exist.' + bcolors.END)

def get_side_from_arg(arg):
    if arg in ['left', '--left', '-l']:
        return 'left'
    elif arg in ['right', '--right', '-r']:
        return 'right'
    else:
        return 'both'

def print_help(command):
    if command == 'mv':
        print()
    elif command == 'size':
        print()
    elif command == 'sauce':
        print()
    elif command == 'cheese':
        print()
    elif command == 'base':
        print()
    elif command == 'config'

# Globals
pizzas = {}
last_branch_added = None
current_branch = None
order_info = {}
order_info_global = {
    'user.firstname': None,
    'user.lastname': None,
    'user.email': None,
    'user.phone': None,
    'delivery.instructions': None,
    'address.street_number': None,
    'address.city': None,
    'address.province': None,
    'address.suite': None,
    'address.additional': None
}

# Regexes
regex_branch_name = re.compile(r'^[\w\d-]+$')

# Reset all variables to their default value
# If the globals above are updated, they should be updated here
def set_defaults():
    global pizzas
    global last_branch_added

    pizzas = {}
    last_branch_added = None
    current_branch = None
    order_info = {}

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
        current_branch = shelf['current_branch']
        order_info = shelf['order_info']
        order_info_global = shelf['order_info_global']

def parse_config(is_global, args):
    config_to_set = []

    if 'global' == is_global:
        config_to_set.append(order_info_global)
        config_to_set.append(order_info[current_branch])
    else:
        config_to_set.append(order_info[current_branch])

    config = args[0]

    if len(args) == 1:
        if config in config_to_set[0]:
            print(config_to_set[0][config])
        else:
            print_help('config')
        return

    value = args[1]
    if config in config_to_set[0]:
        print(bcolors.RED + str(config_to_set[0][config]) + bcolors.END)
        for config_set in config_to_set:
            config_set[config] = value
        print(config_to_set[0][config])
    else:
        print_help('config')

# Argument parsing
def parse_single_arg(arg):
    global pizzas
    if 'init' == arg:
        if len(pizzas) == 0:
            pizzas = {}
            add_new_pizza('master')
        else:
            print(bcolors.RED + 'You have already initiated an order.' + bcolors.END)
            print('You\'ll have to delete your current pizzas to create a new order.')
            print('Try the command ' + bcolors.BOLD + '\'gitpizza branch\' ' + bcolors.END + 'to see your current pizzas.')
    elif 'branch' == arg:
        for branch in pizzas:
            if current_branch == branch:
                print(bcolors.GREEN + '* ' + branch + bcolors.END)
            else:
                print('  ' + branch)
    elif 'merge' == arg:
        pizzas[current_branch].merge()
    elif 'revert' == arg:
        pizzas[current_branch].unmerge()
    elif 'status' == arg:
        print('On branch {0}'.format(current_branch))
        print(pizzas[current_branch].get_status())
    elif 'diff' == arg:
        print(pizzas[current_branch].get_diff())
    elif 'reset' == arg:
        set_defaults()
        print(bcolors.BOLD + 'Your order has been reset.' + bcolors.END)

def parse_multi_args(args):
    if 'checkout' == args[0]:
        if args[1] == '-b' and regex_branch_name.match(args[2]):
            add_new_pizza(args[2])
        elif regex_branch_name.match(args[1]):
            switch_to_branch(args[1])
    elif args[0] == 'mv':
        if len(args) < 3:
            print_help('mv')
            return
        if args[1] == 'size':
            if not pizzas[current_branch].change_size(args[2]):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[2]))
                print_help('size')
        elif args[1] == 'base':
            if not pizzas[current_branch].change_base(args[2]):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[2]))
                print_help('base')
        elif args[1] == 'sauce':
            if not pizzas[current_branch].change_sauce(args[2]):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[2]))
                print_help('sauce')
        elif args[1] == 'cheese' and len(args) :
            if '--' in args[2]:
                side = get_side_from_arg(args[2])
                cheese_arg = args[3]
            else:
                side = 'both'
                cheese_arg = args[2]
            if not pizzas[current_branch].change_cheese(side, cheese_arg):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(cheese_arg))
                print_help('cheese')
        else:
            print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[1]))
    elif args[0] == 'config':
        if args[1] == '--global':
            parse_config('global', args[2:])
        else:
            parse_config('default', args[1:])
    elif args[0] in ['add', 'rm']:
        if len(args) == 3:
            if '--' in args[1]:
                side = get_side_from_arg(args[1])
                topping_arg = args[2]
            else:
                side = 'both'
                topping_arg = args[1]
        elif len(args) == 2:
            side = 'both'
            topping_arg = args[1]
        else:
            print(bcolors.RED + 'fatal:' + bcolors.END + ' could not parse gitpizza {0} args.'.format(args[0]))
            return

        if args[0] == 'add':
            if not pizzas[current_branch].add_topping(side, topping_arg):
                print('fatal: pathspec \'{0}\' did not match any toppings'.format(topping_arg))
        else:
            if not pizzas[current_branch].remove_topping(side, topping_arg):
                print('fatal: pathspec \'{0}\' did not match any toppings'.format(topping_arg))

if len(sys.argv) <= 1:
    print_welcome_message()
elif len(pizzas) == 0 and 'init' != sys.argv[1]:
    print_welcome_message()
elif len(sys.argv) == 2:
    parse_single_arg(sys.argv[1])
else:
    parse_multi_args(sys.argv[1:])

# Save the configuration for the next run
with shelve.open(shelve_fullname, 'c') as shelf:
    shelf['pizzas'] = pizzas
    shelf['last_branch_added'] = last_branch_added
    shelf['current_branch'] = current_branch
    shelf['order_info'] = order_info
    shelf['order_info_global'] = order_info_global
