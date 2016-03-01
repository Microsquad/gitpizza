#!/usr/bin/env python3.5

# Imports
import os
import re
import shelve
import sys
import time

# Terminal colors
class bcolors:
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Available sizes
sizes = ['personal', 'small', 'medium', 'large']
# Available pizza bases
bases = ['pan', 'homestyle', 'edge', 'stuffed', 'thin']
# Available sauces
sauces = ['tomato', 'alfredo', 'beef-gravy', 'indian-butter', 'old-world-tomato']
# Available cheeses
cheeses = ['regular', 'remove', 'light', 'extra']

# Sides that toppings can be added to
sides = {'left', 'right', 'both'}

# List of available meat options
meats = ['pepperoni', 'bacon-crumble', 'bacon', 'ham', 'grilled-chicken-breast', 'italian-sausage', 'mild-sausage', 'beef', 'smokey-maple-bacon']
# List of available veggies options
veggies = ['mushroom', 'green-pepper', 'pineapple', 'red-onions', 'roasted-red-peppers', 'hot-peppers', 'tomatoes', 'marinated-tomatoes', 'black-olives', 'roasted-garlic', 'parmesan']

required_data = ['address.city', 'address.province', 'address.street_number', 'address.street_name', 'user.email', 'user.firstname', 'user.lastname', 'user.phone', 'delivery.payment', ]

valid_data = {'address.province': ['AB', 'BC', 'MB', 'NB', 'NT', 'NL', 'NS', 'ON', 'PE', 'QC', 'SK', 'YT'], 'delivery.payment': ['cash', 'credit', 'debit']}

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

    # Getter methods for class variables
    def get_meats(self):
        return self.meats
    def get_veggies(self):
        return self.veggies
    def get_cheese(self):
        return self.cheese
    def get_size(self):
        return self.size
    def get_base(self):
        return self.base
    def get_sauce(self):
        return self.sauce

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

        if (len(self.meats['left'] | self.meats['right'] | self.veggies['left'] | self.veggies['right'])) == 5:
            print(bcolors.RED + 'fatal:' + bcolors.END + ' you can only have a maximum of 5 toppings.')
            return False

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
            cheese_diff = '\t{:<24}| {}'.format(self.cheese['left'], self.cheese['right'])

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

def click_topping(actions, element, topping_list, topping, side):
    topping_index = topping_list.index(topping)
    topping_x = 450 + int(topping_index % 4) * 100
    topping_y = 500 + int(topping_index / 4) * 100
    topping_x_offset = 0
    if side == 'left':
        topping_x_offset = -65
    elif side == 'right':
        topping_x_offset = 65

    actions.move_to_element_with_offset(element, topping_x, topping_y)
    actions.move_to_element_with_offset(element, topping_x + topping_x_offset, topping_y - 85).click()
    actions.move_to_element_with_offset(element, 15, 200).click()

def perform_order_placement():
    from selenium import webdriver
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys

    # Load the pizza hut webpage
    browser = webdriver.Chrome()
    browser.set_window_position(0, 0)
    browser.set_window_size(800, 700)
    browser.maximize_window()
    print('ordering pizza...')
    browser.get('https://www.pizzahut.ca/#!/home')
    print('entering address...')
    browser.find_element_by_css_selector('.button.ph-primary-button.button-welcome').click()

    # Input the user's address
    browser.execute_script('$("#search_streetnumber_251").click()')
    time.sleep(2)
    actions = ActionChains(browser)
    actions.send_keys(Keys.TAB)
    actions.send_keys(order_info['address.street_number'])
    actions.send_keys(Keys.TAB)
    actions.send_keys(order_info['address.street_name'])
    actions.send_keys(Keys.TAB)
    actions.send_keys(order_info['address.city'])
    actions.send_keys(Keys.TAB)
    actions.send_keys(order_info['address.province'])
    actions.send_keys(Keys.TAB)
    if order_info['address.suite']:
        actions.send_keys(order_info['address.suite'])
    actions.send_keys(Keys.TAB)
    if order_info['address.additional']:
        actions.send_keys(order_info['address.additional'])
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(2)

    # Select the closest store
    print('selecting a store close to you...')
    stores = browser.find_elements_by_class_name('store-selection-row')
    if len(stores) > 0:
        stores[0].click()
    time.sleep(2)

    # Loading pizza page
    for pizza in pizzas:
        print('navigating to pizza...')
        browser.get('https://www.pizzahut.ca/#!/menu/pizza')
        time.sleep(3)
        actions = ActionChains(browser)
        for i in range(10):
            actions.send_keys(Keys.TAB)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        time.sleep(3)

        print('setting pizza size...')
        root_div = browser.find_element_by_xpath('/html/body/div')
        actions = ActionChains(browser)
        actions.move_to_element_with_offset(root_div, 240, 315).click()
        actions.move_to_element_with_offset(root_div, 225, 345).click()
        actions.move_to_element_with_offset(root_div, 215, 610 - 70 * sizes.index(pizzas[pizza].get_size())).click()
        actions.perform()
        time.sleep(2)

        print('setting pizza base...')
        actions = ActionChains(browser)
        actions.move_to_element_with_offset(root_div, 225, 400).click()
        actions.move_to_element_with_offset(root_div, 225, 440 + 50 * bases.index(pizzas[pizza].get_base())).click()
        actions.perform()
        time.sleep(2)

        print('setting pizza sauce...')
        actions = ActionChains(browser)
        actions.move_to_element_with_offset(root_div, 500, 315).click()
        actions.move_to_element_with_offset(root_div, 475, 345).click()
        actions.move_to_element_with_offset(root_div, 475, 390 + sauces.index(pizzas[pizza].get_sauce())).click()
        actions.move_to_element_with_offset(root_div, 500, 315).click()
        actions.perform()

        print('setting meat toppings...')
        actions = ActionChains(browser)
        meat_cache = {'left': pizzas[pizza].get_meats()['left'].copy(), 'right': pizzas[pizza].get_meats()['right'].copy()}
        for meat in meat_cache['left']:
            if meat not in meat_cache['right']:
                click_topping(actions, root_div, meats, meat, 'left')
            else:
                click_topping(actions, root_div, meats, meat, 'both')
        for meat in meat_cache['right']:
            if meat not in meat_cache['left']:
                click_topping(actions, root_div, meats, meat, 'right')
        actions.perform()

        time.sleep(10)

        print('setting veggie toppings...')
        actions = ActionChains(browser)
        actions.move_to_element_with_offset(root_div, 730, 400).click()
        actions.perform()
        actions = ActionChains(browser)
        veggie_cache = {'left': pizzas[pizza].get_veggies()['left'].copy(), 'right': pizzas[pizza].get_veggies()['right'].copy()}
        for veggie in veggie_cache['left']:
            if veggie not in veggie_cache['right']:
                click_topping(actions, root_div, veggies, veggie, 'left')
            else:
                click_topping(actions, root_div, veggies, veggie, 'both')
        for veggie in veggie_cache['right']:
            if veggie not in veggie_cache['left']:
                click_topping(actions, root_div, veggies, veggie, 'right')
        actions.perform()
        time.sleep(10)

        browser.find_element_by_css_selector('.button.ph-default-button.qs-text-button.ng-binding').click()

    print('proceeding to checkout...')
    browser.get('https://www.pizzahut.ca/#!/cart')
    time.sleep(5)
    browser.get('https://www.pizzahut.ca/#!/checkout')
    time.sleep(5)
    browser.get('https://www.pizzahut.ca/#!/showcheckoutguestdetails')
    time.sleep(5)

    # print('submitting user info')
    # actions = ActionChains(browser)
    # actions.send_keys(Keys.TAB)
    # actions.send_keys(Keys.TAB)
    # actions.send_keys(order_info['user.firstname'])
    # actions.send_keys(Keys.TAB)
    # actions.send_keys(order_info['user.lastname'])
    # actions.send_keys(Keys.TAB)
    # actions.send_keys(order_info['user.email'])
    # actions.send_keys(Keys.TAB)
    # actions.send_keys(order_info['user.email'])
    # actions.send_keys(Keys.TAB)
    # actions.send_keys(order_info['user.phone'])

    browser.get('https://www.pizzahut.ca/#!/paymentdetails')

    # Uncomment to actually order a pizza
    # browser.find_element_by_css_selector('.button.ph-default-button.continue-checkout-button.ng-binding')
    time.sleep(2)

    html = browser.execute_script("return document.documentElement.outerHTML")
    total = re.search(r'<td class=\"product-price order-total ng-binding\">(.*?)<\/td>', html).group(1)

    print('pizza ordered! your total is {0}, please be ready to pay by {1}.'.format(total, order_info['delivery.payment']))

    time.sleep(30)

    browser.quit()

# Prints a sick ass pizza
def print_pizza():
    print("""
       _ _        _
  __ _(_) |_ _ __(_)________ _
 / _` | |  _| '_ \ |_ /_ / _` |
 \__, |_|\__| .__/_/__/__\__,_|
 |___/      |_|
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
    current_branch = branch
    print('Initialized basic pizza.')
    print('Switching to branch {0}.'.format(branch))
    print(pizzas[branch].get_status())

def commit_pizzas():
    print('\nYou\'re nearly ready to order. Confirm your branches below.')
    for branch in pizzas:
        print('\n--------------------------------------\nStatus of branch ' + bcolors.GREEN + branch + bcolors.END)
        print(pizzas[branch].get_status())
    print('Ensure your delivery details are correct.\n')
    sorted_order_info = sorted(list(order_info.keys()))
    for info in sorted_order_info:
        print(bcolors.MAGENTA + '  ' + '{:<25}'.format(info + ':') + bcolors.END + str(order_info[info]))
    print('If this looks correct, place your order with ' + bcolors.BOLD + '\'gitpizza push origin master\'' + bcolors.END)

def place_order():
    missing_data = []
    for config in required_data:
        if order_info[config] == None:
            missing_data.append(config)

    if len(missing_data) > 0:
        print(bcolors.RED + 'fatal:' + bcolors.END + ' unable to push to remote. You are missing required data for your order.')
        for data in missing_data:
            valid = ''
            if data in valid_data:
                valid = ': ' + bcolors.GREEN + ', '.join(valid_data[data]) + bcolors.END
            print('missing: ' + bcolors.RED + data + bcolors.END + valid)
        return

    print_pizza()
    perform_order_placement()

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
        print(bcolors.MAGENTA + 'mv' + bcolors.END + ' allows you to rename of the following pizza properties.')
        print('\t' + bcolors.GREEN + 'size: ' + bcolors.END + ', '.join(sizes))
        print('\t' + bcolors.GREEN + 'base: ' + bcolors.END + ', '.join(bases))
        print('\t' + bcolors.GREEN + 'sauce: ' + bcolors.END + ', '.join(sauces))
    elif command == 'config':
        print(bcolors.MAGENTA + 'config' + bcolors.END + ' allows you to define where your pizza will be delivered.')
        print('Add the flag --global to save these options for future orders.')
    elif command == 'push':
        print(bcolors.MAGENTA + 'push' + bcolors.END + ' your pizza to ' + bcolors.BOLD + 'origin master' + bcolors.END + ' to place your order.')
    elif command == 'add':
        print(bcolors.MAGENTA + 'add' + bcolors.END + ' allows you to add any of the following toppings to your pizza.')
        print('\t' + bcolors.GREEN + 'meats: ' + bcolors.END + ', '.join(meats))
        print('\t' + bcolors.GREEN + 'veggies: ' + bcolors.END + ', '.join(veggies))
    elif command == 'rm':
        print(bcolors.MAGENTA + 'rm' + bcolors.END + ' allows you to remove a topping from your pizza')

# Globals
pizzas = {}
last_branch_added = None
current_branch = None
order_info = None
order_info_global = {
    'user.firstname': None,
    'user.lastname': None,
    'user.email': None,
    'user.phone': None,
    'delivery.instructions': None,
    'delivery.payment': None,
    'address.street_number': None,
    'address.street_name': None,
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
shelve_folder = '.gitpizza-shelf'
shelve_name = 'pizza'
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
        config_to_set.append(order_info)
    else:
        config_to_set.append(order_info)

    config = args[0]

    if len(args) == 1:
        if config in config_to_set[0]:
            print(config_to_set[0][config])
        else:
            print_help('config')
        return

    value = args[1]
    if config in valid_data:
        if value not in valid_data[config]:
            print(bcolors.RED + 'fatal: ' + bcolors.END + 'invalid configuration value provided.')
            print(bcolors.GREEN + 'valid: ' + bcolors.END + ', '.join(valid_data[config]))
            return

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
    global order_info
    if 'init' == arg:
        if len(pizzas) == 0:
            pizzas = {}
            add_new_pizza('master')
            order_info = order_info_global.copy()
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
    elif 'clean' == arg:
        print('Cleaning branch ' + current_branch)
        del pizzas[current_branch]
        add_new_pizza(current_branch)
    elif 'merge' == arg:
        pizzas[current_branch].merge()
    elif 'revert' == arg:
        pizzas[current_branch].unmerge()
    elif 'status' == arg:
        print('On branch {0}'.format(current_branch))
        print(pizzas[current_branch].get_status())
    elif 'diff' == arg:
        print(pizzas[current_branch].get_diff())
    elif 'commit' == arg:
        commit_pizzas()
    elif 'reset' == arg:
        set_defaults()
        print(bcolors.BOLD + 'Your order has been reset.' + bcolors.END)
    elif arg in ['mv', 'config', 'push']:
        print_help(arg)

def parse_multi_args(args):
    if 'checkout' == args[0]:
        if args[1] == '-b' and regex_branch_name.match(args[2]):
            add_new_pizza(args[2])
        elif regex_branch_name.match(args[1]):
            switch_to_branch(args[1])
    elif args[0] == 'branch':
        if args[1] == '--delete' and len(args) == 3:
            if args[2] in pizzas:
                if args[2] == current_branch:
                    print(bcolors.RED + 'fatal:' + bcolors.END + ' you cannot delete the branch you are currently on.')
                else:
                    print(bcolors.BOLD + 'Deleting branch ' + args[2] + bcolors.END)
                    del pizzas[args[2]]
        else:
            print_help('branch')
    elif args[0] == 'mv':
        if len(args) < 3:
            print_help('mv')
            return
        if args[1] == 'size':
            if not pizzas[current_branch].change_size(args[2]):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[2]))
                print_help('mv')
        elif args[1] == 'base':
            if not pizzas[current_branch].change_base(args[2]):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[2]))
                print_help('mv')
        elif args[1] == 'sauce':
            if not pizzas[current_branch].change_sauce(args[2]):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[2]))
                print_help('mv')
        elif args[1] == 'cheese' and len(args) :
            if '--' in args[2]:
                side = get_side_from_arg(args[2])
                cheese_arg = args[3]
            else:
                side = 'both'
                cheese_arg = args[2]
            if not pizzas[current_branch].change_cheese(side, cheese_arg):
                print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(cheese_arg))
        else:
            print(bcolors.RED + 'fatal:' + bcolors.END + ' destination {0} is not a directory.'.format(args[1]))
    elif args[0] == 'config':
        if args[1] == '--global':
            parse_config('global', args[2:])
        else:
            parse_config('default', args[1:])
    elif args[0] == 'push':
        if len(args) == 3:
            if args[1] == 'origin' and args[2] == 'master':
                place_order()
                return
        print_help('push')
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
