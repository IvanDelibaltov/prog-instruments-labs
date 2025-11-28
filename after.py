import os
import json


def menu():
    options = {
        1: {"title": "Add new customer details", "method": lambda: add_customer()},
        2: {
            "title": "Modify already existing customer details",
            "method": lambda: modify_customer(),
        },
        3: {"title": "Search customer details", "method": lambda: search_customer()},
        4: {"title": "View all customer details", "method": lambda: view_customers()},
        5: {"title": "Delete customer details", "method": lambda: remove_customer()},
        6: {"title": "Exit the program", "method": lambda: exit_program()},
    }

    print(f"\n\n{' ' * 25}Welcome to Hotel Database Management Software\n\n")

    for num, option in options.items():
        print(f"{num}: {option.get('title')}")
    print()

    options.get(int(input("Enter your choice(1-6): "))).get("method")()


def add_customer():
    first_name = input("\nEnter your first name: \n")
    last_name = input("\nEnter your last name: \n")
    phone_number = input("\nEnter your phone number(without +91): \n")

    print("These are the rooms that are currently available")
    print("1-Normal (500/Day)")
    print("2-Deluxe (1000/Day)")
    print("3-Super Deluxe (1500/Day)")
    print("4-Premium Deluxe (2000/Day)")

    room_type = int(input("\nWhich type you want(1-4): \n"))

    match room_type:
        case 1:
            price_per_day = 500
            room_type_name = "Normal"
        case 2:
            price_per_day = 1000
            room_type_name = "Deluxe"
        case 3:
            price_per_day = 1500
            room_type_name = "Super Deluxe"
        case 4:
            price_per_day = 2000
            room_type_name = "Premium Deluxe"

    days_stay = int(input("How many days you will stay: "))
    total_price = price_per_day * days_stay
    total_price_str = str(total_price)
    print("")

    print("You have to pay ", (total_price_str))
    print("")

    payment_method = input("Mode of payment(Card/Cash/Online): ").capitalize()
    if payment_method == "Card":
        print("Payment with card")
    elif payment_method == "Cash":
        print("Payment with cash")
    elif payment_method == "Online":
        print("Online payment")
    print("")

    with open("Management.txt", "r") as file:
        string = file.read()
        string = string.replace("'", '"')
        dictionary = json.loads(string)

    if len(dictionary.get("Room")) == 0:
        room_number = "501"
    else:
        room_list = dictionary.get("Room")
        last_index = len(room_list) - 1
        last_room = int(room_list[last_index])
        room_number = 1 + last_room
        room_number = str(room_number)

    print("You have been assigned Room Number", room_number)
    print(f"name : {first_name} {last_name}")
    print(f"phone number : +91{phone_number}")
    print(f"Room type : {room_type_name}")
    print(f"Stay (day) : {days_stay}")

    dictionary["First_Name"].append(first_name)
    dictionary["Last_Name"].append(last_name)
    dictionary["Phone_num"].append(phone_number)
    dictionary["Room_Type"].append(room_type_name)
    dictionary["Days"].append(days_stay)
    dictionary["Price"].append(total_price_str)
    dictionary["Room"].append(room_number)

    with open("Management.txt", "w", encoding="utf-8") as file:
        file.write(str(dictionary))

    print("\nYour data has been successfully added to our database.")

    exit_menu()


file_check = os.path.isfile("Management.txt")
if not file_check:
    with open("Management.txt", "a", encoding="utf-8") as file:
        template = {
            "First_Name": [],
            "Last_Name": [],
            "Phone_num": [],
            "Room_Type": [],
            "Days": [],
            "Price": [],
            "Room": [],
        }
        file.write(str(template))


def modify_customer():
    with open("Management.txt", "r") as file:
        string = file.read()
        string = string.replace("'", '"')
        dictionary = json.loads(string)

    room_list = dictionary.get("Room")
    list_length = len(room_list)
    if list_length == 0:
        print("\nThere is no data in our database\n")
        menu()
    else:
        room_number = input("\nEnter your Room Number: ")

        room_list = dictionary["Room"]
        index = int(room_list.index(room_number))

        print("\n1-Change your first name")
        print("2-Change your last name")
        print("3-Change your phone number")

        choice = int(input("\nEnter your choice: "))
        print()

        with open("Management.txt", "w", encoding="utf-8") as file:
            match choice:
                case 1:
                    category = "First_Name"
                case 2:
                    category = "Last_Name"
                case 3:
                    category = "Phone_num"

            user_input = input(f"Enter New {category.replace('_', ' ')}")
            category_list = dictionary[category]
            category_list[index] = user_input
            dictionary[category] = None
            dictionary[category] = category_list

            file.write(str(dictionary))

        print("\nYour data has been successfully updated")
        exit_menu()


def search_customer():
    with open("Management.txt") as file:
        dictionary = json.loads(file.read().replace("'", '"'))

    room_list = dictionary.get("Room")
    list_length = len(room_list)

    if list_length == 0:
        print("\nThere is no data in our database\n")
        menu()
    else:
        room_number = input("\nEnter your Room Number: ")

        room_numbers = dictionary.get("Room")
        index = int(room_numbers.index(room_number))

        first_names = dictionary.get("First_Name")
        last_names = dictionary.get("Last_Name")
        phone_numbers = dictionary.get("Phone_num")
        room_types = dictionary.get("Room_Type")
        days_list = dictionary.get("Days")
        prices = dictionary.get("Price")

        print(f"\nFirst Name: {first_names[index]}")
        print(f"Last Name: {last_names[index]}")
        print(f"Phone number: {phone_numbers[index]}")
        print(f"Room Type: {room_types[index]}")
        print(f"Days staying: {days_list[index]}")
        print(f"Money paid: {prices[index]}")
        print(f"Room Number: {room_numbers[index]}")

        exit_menu()


def remove_customer():
    with open("Management.txt") as file:
        dictionary = json.loads(file.read().replace("'", '"'))

    room_list = dictionary.get("Room")
    list_length = len(room_list)
    if list_length == 0:
        print("\nThere is no data in our database\n")
        menu()
    else:
        room_number = input("\nEnter your Room Number: ")

        room_numbers = dictionary["Room"]
        index = int(room_numbers.index(room_number))

        first_names = dictionary.get("First_Name")
        last_names = dictionary.get("Last_Name")
        phone_numbers = dictionary.get("Phone_num")
        room_types = dictionary.get("Room_Type")
        days_list = dictionary.get("Days")
        prices = dictionary.get("Price")
        room_nums = dictionary.get("Room")

        del first_names[index]
        del last_names[index]
        del phone_numbers[index]
        del room_types[index]
        del days_list[index]
        del prices[index]
        del room_nums[index]

        dictionary["First_Name"] = None
        dictionary["First_Name"] = first_names

        dictionary["Last_Name"] = None
        dictionary["Last_Name"] = last_names

        dictionary["Phone_num"] = None
        dictionary["Phone_num"] = phone_numbers

        dictionary["Room_Type"] = None
        dictionary["Room_Type"] = room_types

        dictionary["Days"] = None
        dictionary["Days"] = days_list

        dictionary["Price"] = None
        dictionary["Price"] = prices

        dictionary["Room"] = None
        dictionary["Room"] = room_nums

        with open("Management.txt", "w", encoding="utf-8") as file:
            file.write(str(dictionary))

        print("Details has been removed successfully")

        exit_menu()


def view_customers():
    with open("Management.txt") as file:
        dictionary = json.loads(file.read().replace("'", '"'))

    room_list = dictionary.get("Room")
    list_length = len(room_list)
    if list_length == 0:
        print("\nThere is no data in our database\n")
        menu()

    else:
        room_numbers = dictionary["Room"]
        total_customers = len(room_numbers)

        index = 0
        while index != total_customers:
            first_names = dictionary.get("First_Name")
            last_names = dictionary.get("Last_Name")
            phone_numbers = dictionary.get("Phone_num")
            room_types = dictionary.get("Room_Type")
            days_list = dictionary.get("Days")
            prices = dictionary.get("Price")
            room_nums = dictionary.get("Room")

            print("")
            print("First Name:", first_names[index])
            print("Last Name:", last_names[index])
            print("Phone number:", phone_numbers[index])
            print("Room Type:", room_types[index])
            print("Days staying:", days_list[index])
            print("Money paid:", prices[index])
            print("Room Number:", room_nums[index])
            print("")

            index = index + 1

        exit_menu()


def exit_program():
    print("")
    print("                             Thanks for visiting")
    print("                                 Goodbye")


def exit_menu():
    print("")
    print("Do you want to exit the program or return to main menu")
    print("1-Main Menu")
    print("2-Exit")
    print("")

    user_input = int(input("Enter your choice: "))
    if user_input == 2:
        exit_program()
    elif user_input == 1:
        menu()


try:
    menu()
except KeyboardInterrupt:
    print("\nexiting...!")
