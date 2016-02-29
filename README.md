# gitpizza

It's like git, but instead of adding files, you add toppings. Commit, push, and your order is placed

## How to use

1. Begin by downloading gitpizza.py (you can download it directly or clone the repository with `git clone https://github.com/Microsquad/gitpizza.git`)
2. Ensure you have write permissions in the directory which `gitpizza.py` is saved, as it creates a shelf for persistence between runs (in a folder `.gitpizza-shelf` if you want to remove it later)
3. Initialize a new order with `python gitpizza.py init`
4. Try some of the other commands below!

## Available Commands

`gitpizza init` Initialize a new order.  
`gitpizza reset` Remove an order and return gitpizza to its initial state.  
`gitpizza add [--left|--right|--both] <topping>` Add a topping to the pizza. Provide either `--left`, `--right` or `--both` (default) to add the topping to a specific side.  
`gitpizza rm [--left|--right|--both] <topping>` Remove a topping from the pizza. Provide either `--left`, `--right` or `--both` (default) to remove the topping only from a specific side.  
`gitpizza merge` Add any toppings which are missing from the left side of the pizza to the right and vice versa.  
`gitpizza revert` Under a merge, so long as the pizza has not been altered since it was merged.  
`gitpizza checkout -b <branch-name>` Add a new pizza to the order.  
`gitpizza checkout <branch-name>` Return to editing a certain pizza in the order.  
`gitpizza branch` List the pizzas in the order, and highlight the current branch.  
`gitpizza branch --delete <branch-name>` Remove a branch (pizza) from the order.  
`gitpizza mv [size|sauce|base] <option>` Update a property of the pizza.  
`gitpizza diff` See the differences between the left and right sides of the current branch (pizza).  
`gitpizza status` See the properties and toppings on the current pizza.  
`gitpizza clean` Reset the current pizza to its initial state. Cannot be undone.
`gitpizza commit` View the properties of all of the branches in the order and check the order details.  
`gitpizza push origin master` Begins the process of ordering a pizza. This process will stop just before finishing a pizza order, to ensure orders are not accidentally misplaced. Use with care!

## nwHacks 2016 Entry

Visit the Devpost entry [here](http://devpost.com/software/gitpizza).

### Inspiration

gitpizza was inspired by a late night development push and a bout of hunger. What if you could order a pizza without having to leave the comfort of your terminal?

### What it does

gitpizza is a CLI based on git which allows you to create a number of pizzas (branches), add toppings (files), configure your address and delivery info, and push your order straight to Pizza Hut.

### How I built it

Python is bread and butter of gitpizza, parsing the provided arguments and using selenium to automatically navigate through the Pizza Hut website.

### Challenges I ran into

Pizza Hut's website is mostly created with angular, meaning selenium would retrieve a barebones HTML page and it would later be dynamically populated with JavaScript. But selenium didn't see these changes, so finding elements by ids and such was impossible. That, along with the generic names and lack of ids in general on the website meant that my only solution was the physically move the mouse and click on pixel-perfect positions to add toppings and place the user's order.

### Accomplishments that I'm proud of

Just the amount of commands that gitpizza supports. ```gitpizza init``` to start a new order, ```gitpizza checkout -b new-pizza``` to create a second pizza, ```gitpizza add --left pepperoni``` to add pepperoni to only the left half of your pizza, and ```gitpizza diff``` to see the differences between each side of your pizza.
