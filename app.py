from models import Base, session, Product, engine
import csv, time
from datetime import datetime
from decimal import Decimal


def menu():
    while True:
        print('''
              \nProducts
              \r'v' to view the details of a single product
              \r'a' to add a new product
              \r'b' to make a backup of the entire contents of the database
              \r'c' to exit
              ''')
        choice = input('What would you like to do? ')
        if choice in ['v', 'a', 'b', 'c']:
            return choice
        else:
            input('''
                  \rPlease choose 'v', 'a', 'b' or 'c'.
                  \rPress ENTER to try again
                    ''')


def clean_price(price_str):
    try:
        if '$' in price_str:
            price = price_str.split('$')
            price_float = Decimal(price[1])
        else:
            price_float = Decimal(price_str)
    except ValueError:
        '''
        \rValue Error:
        \rPlease enter the price without the '$',
        like: 1.50
        \rPress enter to try again
        '''
        return
    return int(price_float * 100)


def clean_date(date):
    try:
        date_cleaned = datetime.strptime(date, "%m/%d/%Y")
    except TypeError:
        '''
        \rDate Error:
        \rPlease enter the date in month/day/year format,
        \rex. 01/01/2018
        '''
    return date_cleaned


def clean_choice(choice, options):
    try:
        int_choice = int(choice)
    except ValueError:
        input('''
            \rPlease enter a valid number 
            \rPress enter to continue
            \r
        ''')
    else:
        if int_choice in options:
            return int_choice
        else:
            input('''
                \rYour choice is not one of the options available,
                \rPress enter to try again
                \r
            ''')


def find_product():
    current_products = []
    for product in session.query(Product):
        current_products.append(product.product_id)
    choosing = True
    while choosing:
        choice = input(f'''
                \rProducts: {current_products}
                \rWhich product would you like do view? 
                \r''')
        cleaned_choice = clean_choice(choice, current_products)
        if type(cleaned_choice) == int:
            choosing = False
    the_product = session.query(Product).filter(Product.product_id==choice).first()
    print(f'''
        \rProduct: {the_product.product_name}
        \rPrice: ${'{:.2f}'.format(the_product.product_price /100)}
        \rQuantity: {the_product.product_quantity}
        \rDate Updated: {the_product.date_updated.strftime("%m/%d/%Y")}
    ''')
    input('\nPress enter to continue ')


def add_product():
    name = input('''
            \r---Adding Product---
            \rName: ''')
    adding_price = True
    while adding_price:
        price = input('Price (ex. $1.50): ')
        price_cleaned = clean_price(price)
        if type(price_cleaned) == int:
            adding_price = False
    quantity = input('Quantity: ')
    adding_date = True
    while adding_date:
        date = input('Date (ex. 01/01/2018): ')
        date_cleaned = clean_date(date)
        if type(date_cleaned) == datetime:
            adding_date = False
    db_product = session.query(Product).filter(Product.product_name==name).one_or_none()
    if db_product == None:
        new_product = Product(product_name=name, product_price=price_cleaned, product_quantity=quantity, date_updated=date_cleaned)
        session.add(new_product)
    else:
        if db_product.date_updated < datetime.date(date_cleaned):
            db_product.product_price = price_cleaned
            db_product.product_quantity = quantity
            db_product.date_updated = date_cleaned
    session.commit()
    


def create_backup():
    with open('inventory.csv') as csvfile, open('inventory_backup.csv', 'w', encoding='UTF8') as file:
        reader = csv.reader(csvfile)
        writer = csv.writer(file)
        for row in reader:
            writer.writerow(row)


def add_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            if row[0] == 'product_name':
                continue
            db_product = session.query(Product).filter(Product.product_name==row[0]).one_or_none()
            if db_product == None:
                name = row[0]
                price = clean_price(row[1])
                quantity = row[2]
                date_updated = clean_date(row[3])
                new_product = Product(product_name=name, product_price=price, product_quantity=quantity, date_updated=date_updated)
                session.add(new_product)
            else:
                if db_product.date_updated < datetime.date(clean_date(row[3])):
                    db_product.product_price = clean_price(row[1])
                    db_product.product_quantity = row[2]
                    db_product.date_updated = clean_date(row[3])
        session.commit()
    

def app():
    running = True
    while running:
        choice = menu()
        if choice == 'v':
            # view details
            find_product()

        if choice == 'a':
            # add product
            add_product()

        if choice == 'b':
            # make a backup
            create_backup()
            print('\nBackup Successful')
            time.sleep(1.5)

        if choice == 'c':
            print('\nGoodbye\n')
            time.sleep(1.5)
            running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()
    app()

    