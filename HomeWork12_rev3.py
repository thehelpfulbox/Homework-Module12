from collections import UserDict
from datetime import datetime, date
from itertools import islice
import json


################# Classes #################

class Field:
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError("Value must be string")
        else:
            self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

    def __eq__(self, obj):
        return self.value == obj.value

    def __hash__(self):
        return hash(self.value)



class Name(Field):
    pass

class Phone(Field):
    def __init__(self, phone = None):
        super().__init__(phone)
        self.__phone = None
        self.phone = phone

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        value = str(value)
        if len(value) <= 5:
            raise ValueError("Phone number must contain more than 5 digits") 
        self.__phone = str(value)


class Birthday(Field):
    def __init__(self, bday=None):
        super().__init__(bday)
        self.__bday = None
        self.bday = bday

    @property
    def bday(self):
        return f"{self.__bday}"

    @bday.setter
    def bday(self, value):
        try:
            datetime.strptime(value, "%d %B %Y")
            self.__bday = value
        except ValueError:
            raise ValueError(f"Write birthday in format 01 January 2002") from None

class Record:
    def __init__(self, name: Name, phones: list[Phone] = None, bday = None):
        self.name = name
        self.phones = phones
        self.bday = bday

    def add_phone(self, phone: Phone):
        self.phones.append(str(phone))
        return f"Contact {self.name} with phone number {phone} has been added"

    def add_bday(self, bday: Birthday):
        self.bday = bday
        return f"Birthday {bday} has been added to the contact {self.name}"

    def del_phone(self, phone: Phone):
        for phone in self.phones:
            self.phones.remove(phone)
            return f"Phone number {phone} has been deleted from contact {self.name}"
        return f"{phone} not in list"

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        if old_phone in self.phones:
            self.del_phone(old_phone)
            self.add_phone(new_phone)
            return f"Phone number {old_phone} has been substituted with {new_phone} for contact {self.name}"
        return f"{old_phone} not in list"


    def days_to_birthday(self):
        if self.bday:
            bd = datetime.strptime(self.bday, "%d %B %Y")
            today = date.today()
            current_year_birthday = date(today.year, bd.month, bd.day)
            if current_year_birthday < today:
                current_year_birthday = date(today.year + 1, bd.month, bd.day)
            delta = current_year_birthday - today
            return delta.days
        return None


    def __str__(self):
        return f"{str(self.name)}, {self.phones}, {str(self.bday) if self.bday else ''}"

    def __repr__(self):
        return str(self)



class Addressbook(UserDict):

    def add_record(self, record: Record):
        if self.get(record.name.value):
            return f"{record.name.value} is already in contacts"
        self.data[record.name.value] = record
        info = "{} with phone {} {} was successfully added to contacts"
        return info.format(record.name.value, record.phones, f"and birthday {record.bday}" if record.bday else "")

    def show_all(self):
        # return self.data
        result = []
        for record in self.values():
            result.append(str(record))
        return "\n".join(result)

    def phone(self, name):
        try:
            return self.data[name]
        except KeyError:
            return f"Contact {name} is absent"


    def iterator(self, page=None):
        start = 0
        while True:
            result = list(islice(self.data.items(), start, start + page))
            if not result:
                break
            yield result
            start += page


    def to_dict(self):
        data = {}
        for value in self.data.values():
            data.update({str(value.name): {"name": str(value.name),
                                            "phones":[str(p) for p in value.phones],
                                            "bday": str(value.bday)}})
        return data

    def from_dict(self, data):
        for name in data:
            rec = data[name]
            self.add_record(Record(Name(rec["name"]),
                                    [Phone(p) for p in rec["phones"]],
                                    None if rec["bday"] == None else Birthday(rec["bday"])))

    def search(self, param):
        if len(param) < 3:
            return "Param should be >= 3 symbols"
        result = []
        for record in self.values():
            if param in str(record).lower():
                result.append(str(record))
        return "\n".join(result)


    def __repr__ (self):
        return str(self)

    def __str__(self):
        results = []
        for record in self.values():
            results.append(str(record))
        return "\n".join(results)


################# Functions #################

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (IndexError, TypeError, ValueError):
            return f'{func.__name__:} - Command was entered incorrectly.'
        except KeyError:
            return "Can't find such name in the database."
    return inner


@input_error
def add_new_contact(*data):
    name = Name(data[0].lower().capitalize())
    raw_phone = "".join(data[1:])
    sanitized_phone = ""
    for i in raw_phone:
        if not i.isdigit():
            continue
        else:
            sanitized_phone += i
    if len(sanitized_phone) == 0:
        return f"Can't create the record '{name}'. The number that you entered does not contain any digits."
    else:
        phone = Phone(sanitized_phone)
    record = contacts.get(name.value)
    if record:
        record.add_phone(phone)
        return f'Phone number {phone} was added successfully to contact {name}'
    record = Record(name, [phone])
    contacts.add_record(record)
    return f'Contact {name} with phone number {phone} was added successfully'


@input_error
def change_phone(*data):
    name = Name(data[0].lower().capitalize())
    old_phone = Phone(data[1])
    new_phone = Phone(data[2])
    rec = contacts.get(str(name))
    if rec:
        return rec.change_phone(old_phone, new_phone)
    return f"No contact with name {name}"


@input_error
def show_phone(*result):
    name = Name(result[0].lower().capitalize())
    if name.value in contacts.data:
        for key, val in contacts.data.items():
            record = contacts.data[key]
            if name.value == key:
                return f"{name.value}: {', '.join(str(phone) for phone in record.phones)}"
    return f'No contact with name "{name}" was found in contacts'

@input_error
def show_all_contacts(page):
    if contacts:
        results = ""
        for record in contacts.iterator(int(page)):
            results += ("\n" + str(record))
        return results
    else:
        return "You have no contacts yet"    


@input_error
def add_birthday(*data):
    name = Name(data[0].lower().capitalize())
    rec = contacts.get(str(name))
    birthdate = Birthday(data[1])
    if rec:
        return rec.add_bday(birthdate)
    return f"No contact with name {name}"

@input_error
def find(data):
    return contacts.search(data)

@input_error
def days_to_bd(data):
    name = Name(data.lower().capitalize())
    rec = contacts.get(str(name))
    # print(f"name:{str(name)}, rec:{str(rec)}")
    # print(f"rec.bday:{rec.bday}")
    if not rec:
        return f'No contact with name "{name}"'
    if rec and (not rec.bday):
        return f'The contact "{name}" has no birthdate in records'
    return rec.days_to_birthday()


@input_error
def hello(*result):
    return """How can I help you?
        - To ADD or UPDATE contact, type:               <add name number>
        - To ADD or UPDATE birthday, type:              <birthday name birth_date>
        - To FIND contacts by parameter, type:          <find parameter>
        - To show number of DAYS TO BIRTHDAY, type:     <when name>
        - To show the PHONES of the person, type:       <phone name>
        - To show ALL CONTACTS, type:                   <show all #_of_records_per_page>
        - To CHANGE phone, type:                        <change name old_number new_number>
        - To SAVE the address book into file, type:     <save>
        - To LOAD the address book from file, type:     <load>
        - To EXIT, type:                                <exit> or <close> or <good bye>"""


@input_error
def end(*result):
    return "Good bye!"


def unknown_input(*command):
    return "Unknown command"


def save(*command):
    # перетворюємо вміст адресної книги в словниковий формат і записуємо його в файл json
    storage = "data.json"
    with open(storage, "w") as f:
        json.dump(contacts.to_dict(), f)
    return f"The address book has been saved to '{storage}' file"

def load(*command):
    # створюємо порожню адресну книгу, в неї запишемо вміст файлу json
    new_contacts = Addressbook()

    # читаємо файл json, перетворюємо його зі словникового формату в формат записів адресної книги (метод from_dict)
    # і записуємо в адресну книгу у відповідні поля
    storage = "data.json"

    with open(storage, "r") as f:
        data = json.load(f)
        new_contacts.from_dict(data)
    print([i for i in new_contacts.data.items()])
    return f"{'*' * 80}\nThe address book has been loaded from '{storage}' file"


COMMANDS = {'hello': hello,
            'add': add_new_contact,
            'birthday': add_birthday,
            'good bye': end,
            'exit': end,
            'close': end,
            'find': find,
            'show all': show_all_contacts,
            'change': change_phone,
            'phone': show_phone,
            'when': days_to_bd,
            'save': save,
            'load': load,
            }


def parser(user_input:str):
    user_input = user_input.lower()

    if user_input.startswith("add"):
        return add_new_contact, user_input.removeprefix("add").strip().split()
    elif user_input.startswith("birthday"):
        return add_birthday, user_input.removeprefix("birthday").strip().split(" ", 1)
    elif user_input.startswith("hello"):
        return hello, user_input.removeprefix("hello").strip().split()
    elif user_input.startswith("when"):
        return days_to_bd, user_input.removeprefix("when").strip().split()
    elif user_input.startswith("find"):
        return find, user_input.removeprefix("find").strip().split(" ", 1)
    elif user_input.startswith("change"):
        return change_phone, user_input.removeprefix("change").strip().split()
    elif user_input.startswith("phone"):
        return show_phone, user_input.removeprefix("phone").strip().split()
    elif user_input.startswith("show all"):
        return show_all_contacts, user_input.removeprefix("show all").strip().split()
    elif user_input.startswith("save"):
        return save, user_input.removeprefix("save").strip().split()
    elif user_input.startswith("load"):
        return load, user_input.removeprefix("load").strip().split()
    elif user_input.startswith("exit") or user_input.startswith("close") or user_input.startswith("good bye"):
        return end, user_input
    else:
        return unknown_input, user_input


def main():
    print(hello())
    while True:
        user_input = (input(">>>")) 
        command, data = parser(user_input)
        print(command(*data))
        if command == end:
            break
            

if __name__ == "__main__":

    contacts = Addressbook()

    # створюємо кілька записів
    record1 = Record(Name("Nick"), ["8976237632"], "25 November 2003")
    record2 = Record(Name("Lara"), ["98265619187"], "13 January 1988")
    record3 = Record(Name("Volodymyr"), ["992775151116"], "29 february 2020")
    record4 = Record(Name("Hiba"), ["9111117689236"], "03 February 1984")
    record5 = Record(Name("Zayn"), ["118873254235"], "10 March 1985")
    record6 = Record(Name("Alex"), ["22766427682"], "16 April 1983")
    record7 = Record(Name("Adrien"), ["3872365238187"], "21 May 1989")
    record8 = Record(Name("Abdel"), ["427127422276"], "23 June 1994")
    record9 = Record(Name("Serhiy"), ["52255366655"], "13 July 1977")
    record10 = Record(Name("Karo"), ["6632666666288"], "25 August 1978")
    record11 = Record(Name("Egle"), ["7177771333277"], "28 September 1982")
    record12 = Record(Name("Dan"), ["81213885239588"], "30 October 1984")
    record13 = Record(Name("Deepak"), ["991191240204"], "31 December 1981")

    contacts.add_record(record1)
    contacts.add_record(record2)
    contacts.add_record(record3)
    contacts.add_record(record4)
    contacts.add_record(record5)
    contacts.add_record(record6)
    contacts.add_record(record7)
    contacts.add_record(record8)
    contacts.add_record(record9)
    contacts.add_record(record10)
    contacts.add_record(record11)
    contacts.add_record(record12)
    contacts.add_record(record13)

    main()



