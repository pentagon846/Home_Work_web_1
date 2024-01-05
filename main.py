import pickle
from collections import UserDict
from datetime import datetime
from abc import ABC, abstractmethod


class Field:
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return str(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value=None):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not isinstance(self._value, str) or len(self._value) != 10 or not self._value.isdigit():
            raise ValueError("Invalid phone number format")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate()


class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)
        self.validate_b()

    def validate_b(self):
        try:
            date_value = datetime.strptime(self._value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please provide Year-Month-Day.")

        if not (1 <= date_value.month <= 12 and 1 <= date_value.day <= 31):
            raise ValueError("Invalid date. Month should be between 1 and 12, day between 1 and 31.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate_b()

    def __str__(self):
        return self._value


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def search(self, query):
        matches = []
        for name, record in self.data.items():
            if query.lower() in name.lower():
                matches.append(record)
            for phone in record.phones:
                if query in phone.value:
                    matches.append(record)
        return matches

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, item_number):
        counter = 0
        result = ""
        for item, record in self.data.items():
            result += f"{item}: {record}\n"
            counter += 1
            if counter >= item_number:
                yield result
                counter = 0
                result = ""
        if result:
            yield result

    def __str__(self):
        records_str = ',\n'.join(f"{name}: {record}" for name, record in self.data.items())
        return f"{{\n{records_str}\n}}"

    def save_bin(self, name):
        with open(name, 'wb') as file:
            pickle.dump(self.data, file)

    def load_bin(self, name):
        try:
            with open(name, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print(f"File '{name}' not found.")


class Record(ABC):
    @abstractmethod
    def display(self):
        pass


class Contact(Record):
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone) for phone in (phones or [])]
        self.birthday = birthday

    def display(self):
        # print("Displaying record")
        print(f'Name: {self.name.value}')

    def __str__(self):
        if self.birthday:
            return (f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)},"
                    f" birthday: {self.birthday}")
        else:
            return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        if phone not in self.phones:
            self.phones.append(phone)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == str(phone_number):
                return phone
        return None

    def edit_phone(self, old, new):
        old = Phone(old)
        new = Phone(new)
        flag = True
        for phone in self.phones:
            if phone.value == old.value:
                index = self.phones.index(phone)
                self.phones[index] = new
                flag = False
        if flag:
            raise ValueError

    def remove_phone(self, phone):
        new_phone = Phone(phone)
        for num in self.phones:
            if num.value == new_phone.value:
                self.phones.remove(num)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        trans = datetime.strptime(str(self.birthday), "%Y-%m-%d")
        next_birthday = datetime(today.year, trans.month, trans.day)
        if today > next_birthday:
            next_birthday = datetime(today.year + 1, trans.month, trans.day)
        days_left = (next_birthday - today).days
        return f"{days_left} days left until birthday {self.name.value}"


class UserInterface(ABC):
    @abstractmethod
    def display_menu(self):
        pass

    @abstractmethod
    def get_choice(self):
        pass


class ConsoleUserInterface(UserInterface):

    def display_menu(self):
        print('add. add Record')
        print('view. view all Records')
        print('find. find number')
        print('search. search for contacts on partial matches in names')
        print('edit. edit phone number')
        print('delete. delete Record')
        print('save. save the address book')
        print('load. load address book from disc')
        print('exit')

    def get_choice(self):
        # print('\n choice you command:  ')
        return input('choice your command:  ')


def main():
    book = AddressBook()

    try:
        book.load_bin('address_book.bin')
    except FileNotFoundError:
        pass
        # print(f"Error loading address book from binary file: {e}")

    user_interface = ConsoleUserInterface()

    while True:
        user_interface.display_menu()
        choice = user_interface.get_choice()

        if choice == 'add':
            name = input('Enter Name: ')
            while True:
                phone = input('Enter phone number: ')
                try:
                    Phone(phone)
                    break
                except ValueError:
                    print(f'Invalid phone number,\n pleas enter correct number')

            birthday = input('Enter birthday data in format YYY-MM-DD: ')

            record = Contact(name, phones=[phone], birthday=birthday)
            book.add_record(record)

            print('Contact saved successful')

        elif choice == 'view':
            if not book:
                print("book is empty!")
            else:
                print('\n All records:')
                print(book)
        elif choice == 'find':
            name = input('Enter name to find: ')
            record = book.find(name)
            if record:
                print(f'Record found for {name}: {record}:')
            else:
                print(f'No record find for {name}')

        elif choice == 'search':
            query = input('Enter the search query: ')
            matches = book.search(query)
            if matches:
                print('Matching records:')
                for match in matches:
                    print(match)
            else:
                print('No matching records found.')

        elif choice == 'edit':
            print('enter name for edit number: ')
            name = input('Enter name: ')
            record = book.find(name)
            if record:
                while True:
                    old_phone = input('Enter Old Phone Number: ')
                    new_phone = input('Enter New Phone Number: ')
                    try:
                        record.edit_phone(old_phone, new_phone)
                        print('Phone number updated successfully!')
                        break
                    except ValueError:
                        print(f'phone is not correct!')
            else:
                print(f'Record with name {name} not found!')

        elif choice == 'save':
            name = input('Enter the name of the binary file to save: ')
            book.save_bin(name)
            print(f'Address book saved to {name} successfully!')

        elif choice == 'load':
            name = input('Enter the name of the binary file to load: ')
            try:
                book.load_bin(name)
                print(f'Address book loaded from {name} successfully!')
            except Exception as e:
                print(f"Error loading address book from binary file: {e}")

        elif choice == 'delete':
            name = input('Enter Name to delete: ')
            book.delete(name)
            print('Record deleted successfully!')

        elif choice == 'exit':
            print('Exiting...')
            break
        else:
            print('Invalid choice. Please enter you command!: ')


if __name__ == '__main__':
    main()
