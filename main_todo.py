import json
import datetime
from enum import Enum
import uuid


def parse_date(date: str):
    return datetime.datetime.strptime(date, '%Y-%m-%d')


def format_date(date: datetime.datetime):
    return date.strftime('%Y-%m-%d')


def print_task(task):
    return f'Nazwa zadania: {task.name},\n' \
        f'opis zadania: {task.description},\n' \
        f'data dodania: {format_date(task.current_time)},\n ' \
        f'data zakończenia: {format_date(task.end_date)},\n' \
        f'STATUS: {task.status}.'


# def find_idx_by_uuid(task_list, uuid):    # Znajduje indeks zadania po uuid    to jest do listy, ja mam słownik
#     for single_task_obj in task_list:
#         if single_task_obj == uuid:
#             return single_task_obj


class Task:
    def __init__(self, name, description, current_time, end_date, status,id):
        self.name = name
        self.description = description
        self.current_time = current_time
        self.end_date = end_date
        self.status = status
        self.id = id


    def copy(self, name=None, description=None, end_date=None, status=None):
        new_name = self.name if name is None else name
        new_description = self.description if description is None else description
        new_end_date = self.end_date if end_date is None else end_date
        new_status = self.status if status is None else status
        current_time = self.current_time
        id = self.id
        return Task(new_name, new_description, current_time,new_end_date, new_status, id)




    def serialize(self):
        self_dict = {
            'name': self.name,
            'description': self.description,
            'current_time': format_date(self.current_time),
            'end_date': format_date(self.end_date),
            'status': self.status.value,
            'id': str(self.id)
        }
        return json.dumps(self_dict)  # powstaje string

    @staticmethod
    def deserialize(string):
        self_dict = json.loads(string)
        current_time = parse_date(self_dict['current_time'])
        end_date = parse_date(self_dict['end_date'])
        status = Status(self_dict['status'])
        id = uuid.UUID(self_dict['id'])
        return Task(self_dict['name'], self_dict['description'], current_time, end_date, status, id)


class Status(Enum):
    ACTIVE = 1
    DONE = 2
    EXPIRED = 3
    CANCELED = 4

    def __str__(self):
        if self == Status.ACTIVE:
            return 'AKTYWNE'
        elif self == Status.DONE:
            return 'ZROBIONE'
        elif self == Status.EXPIRED:
            return 'PO TERMINIE'
        elif self == Status.CANCELED:
            return 'ANULOWANE'


class TaskActions:
    def __init__(self, file_path):
        self.file_path = file_path

    # def update_status(self):
    #     current_time = datetime.datetime.now
    #     end_date

    def read_all_tasks(self):
        tasks_by_uuid = {}                              # słownik
        with open(self.file_path, 'r') as file:
            while True:
                single_task_str = file.readline()
                if single_task_str == '':
                    break
                deserialized_task = Task.deserialize(single_task_str)
                tasks_by_uuid [deserialized_task.id] = deserialized_task
        return tasks_by_uuid

    def add_task(self, new_task: Task):
        with open(self.file_path, 'a') as file:
            file.write(new_task.serialize() + '\n')



    def menu(self):

        while True:
            choice = int(input('Wpisz odpowiednią cyfrę, aby wybrać akcję:\n' + \
                               ' 1 - Dodaj nowe zadanie.\n 2 - Zobacz aktywne zadania.\n' + \
                               ' 3 - Archiwum zadań.\n 4 - Wyjdź.\n'))

            if choice == 1:                             #Dodaj nowe zadanie
                name = input('Podaj nazwę zadania.\n')
                description = input('Opisz zadanie.\n')
                current_time = datetime.datetime.now()
                end_date_input = input('Podaj datę zakończenia (rrrr-mm-dd):')
                end_date = parse_date(end_date_input)
                status = Status.ACTIVE
                id = uuid.uuid4()

                new_task = Task(name, description, current_time, end_date, status, id)
                self.add_task(new_task)

                continue


            elif choice == 2:                           # Zobacz aktywne zadania
                while True:
                    task_dict_by_uuid = self.read_all_tasks()
                    active_tasks_list = list(filter(lambda single: single.status == Status.ACTIVE, task_dict_by_uuid.values()))
        # alternatywnie:  active_tasks_list = [single for single in task_dict_by_uuid.values() if single.status == Status.ACTIVE]

                    for index, single in enumerate(active_tasks_list):  #numeruje poszczególne obiekty typu Task
                        print(index+1)
                        print(print_task(single))

        #TODO dodać opcje wyboru działania

                    task_choice = input('\n Podaj numer zadania, które chcesz zmodyfikować lub wciśnij ENTER, aby powrócić. \n')

                    if task_choice == '': #wraca do poprzedniego menu
                        break
                    else:
                        try:
                            task_index_choice = int(task_choice) -1
                            single_task_uuid = active_tasks_list[task_index_choice].id  # wyciąga id zadania, które zostało wybrane
                            continue
                            # przenosi do kolejnego menu
                        except:
                            print('To nie jest poprawna komenda.')
                            break






# TODO wyszukuje odpowiednie zadanie po id w task_list

            single_task_action_choice = int(input('Wpisz odpowiednią cyfrę, aby wybrać akcję:\n '
                                     '1 - Oznacz zadanie jako wykonane. \n '
                                     '2 - Zmień szczegóły zadania. \n'
                                     '3 - Usuń zadanie. \n'
                                     '4 - Wróć. \n'))

            # if single_task_action_choice == 1:
            #
            #     status = Status.DONE
            #
            # elif single_task_action_choice == 2:
            #
            #
            # elif single_task_action_choice == 3:
            #
            # elif single_task_action_choice == 4:
            #     return False


            # return True

                elif choice == 3:
                    task_dict_by_uuid = self.read_all_tasks()
                    for single in task_dict_by_uuid:
                        if single.status != Status.ACTIVE:
                            print (print_task(single))
                    continue

                elif choice == 4:
                    break  # Wyjdź





if __name__ == '__main__':
    file_path = input('Podaj ścieżkę do pliku z zadaniami.\n')
    actions = TaskActions(file_path)
    #    actions.update_status()
    while actions.menu():
        pass

# TODO action.update_status
# TODO numerki
