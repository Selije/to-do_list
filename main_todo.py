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
        f'data dodania: {format_date(task.current_time)},\n' \
        f'data zakończenia: {format_date(task.end_date)},\n' \
        f'STATUS: {task.status}.\n'


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
        return json.dumps(self_dict)

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

    def __str__(self):
        if self == Status.ACTIVE:
            return 'AKTYWNE'
        elif self == Status.DONE:
            return 'ZROBIONE'
        elif self == Status.EXPIRED:
            return 'PO TERMINIE'


class TaskActions:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tasks_by_id = self.read_all_tasks()

    def update_status(self):
        current_time = datetime.datetime.now()
        task_dict_by_id = self.tasks_by_id
        expired_tasks_list = list(filter(lambda single: single.status == Status.ACTIVE and
                                                        single.end_date < current_time, task_dict_by_id.values()))
        reactivated_tasks_list = list(filter(lambda single: single.status == Status.EXPIRED and
                                                            single.end_date > current_time, task_dict_by_id.values()))
        for single in expired_tasks_list:
            self.task_change_and_save(single.id, status=Status.EXPIRED)

        for single in reactivated_tasks_list:
            self.task_change_and_save(single.id, status=Status.ACTIVE)

    def read_all_tasks(self):
        tasks_by_id = {}
        try:
            with open(self.file_path, 'r') as file:
                while True:
                    single_task_str = file.readline()
                    if single_task_str == '':
                        break
                    deserialized_task = Task.deserialize(single_task_str)
                    tasks_by_id [deserialized_task.id] = deserialized_task
        except:
            with open(self.file_path, 'w'):
                pass
        return tasks_by_id

    def add_task(self, new_task: Task):
        with open(self.file_path, 'a') as file:
            file.write(new_task.serialize() + '\n')

    def save_dict(self):
        with open(self.file_path, 'w') as file:
            for dict_task in self.tasks_by_id.values():
                file.write(dict_task.serialize() + '\n')

    def handle_task_adding(self):
        name = input('Podaj nazwę zadania.\n')
        description = input('Opisz zadanie.\n')
        current_time = datetime.datetime.now()
        end_date_input = input('Podaj datę zakończenia (rrrr-mm-dd): \n')
        end_date = parse_date(end_date_input)
        status = Status.ACTIVE
        id = uuid.uuid4()

        new_task = Task(name, description, current_time, end_date, status, id)
        self.tasks_by_id[new_task.id] = new_task
        self.save_dict()

    def handle_task_body(self):
        while True:
            active_tasks_list = list(
                filter(lambda single: (single.status == Status.ACTIVE) or (single.status == Status.EXPIRED),
                       self.tasks_by_id.values()))

            for index, single in enumerate(active_tasks_list):
                print(f'Numer zadania: {index+1}')
                print(print_task(single))

            task_choice = input('Podaj numer zadania, które chcesz zmodyfikować lub wciśnij ENTER, aby powrócić.')
            print('')

            if task_choice == '':
                break
            else:
                try:
                    task_index_choice = int(task_choice) - 1
                    single_task_id = active_tasks_list[task_index_choice].id
                except:
                    print('To nie jest poprawna komenda. \n')
                    continue

                single_task_action_choice = int(input('Wpisz odpowiednią cyfrę, aby wybrać akcję:\n'
                                                      ' 1 - Oznacz zadanie jako wykonane. \n'
                                                      ' 2 - Zmień szczegóły zadania. \n'
                                                      ' 3 - Usuń zadanie. \n'
                                                      ' 4 - Wróć. \n'))

                if single_task_action_choice == 1:

                    self.task_change_and_save(single_task_id, status=Status.DONE)
                    print('Zadanie zostało oznaczone jako wykonane. \n')
                    break

                elif single_task_action_choice == 2:
                    changes_menu = int(input(' 1 - Zmień nazwę zadania. \n'
                                             ' 2 - Zmień opis zadania. \n'
                                             ' 3 - Zmień datę zakończenia. \n'
                                             ' 4 - Wróć. \n'))

                    if changes_menu == 1:
                        new_name = input('Podaj nową nazwę: \n')
                        self.task_change_and_save(single_task_id, name=new_name)

                    elif changes_menu == 2:
                        new_description = input('Podaj nowy opis: \n')
                        self.task_change_and_save(single_task_id, description=new_description)

                    elif changes_menu == 3:
                        new_end_date = input('Podaj datę zakończenia: \n')
                        self.task_change_and_save(single_task_id, end_date=parse_date(new_end_date))
                        self.update_status()

                    else:
                        break

                elif single_task_action_choice == 3:
                    self.delete_task(single_task_id)
                    break

                elif single_task_action_choice == 4:
                    break

    def delete_task(self, single_task_id):
        del self.tasks_by_id[single_task_id]
        self.save_dict()
        print('Zadanie zostało usunięte. \n')

    def task_change_and_save(self, single_task_id, name=None, description=None, end_date=None, status=None):
        update_task = self.tasks_by_id[single_task_id]
        self.tasks_by_id[single_task_id] = update_task.copy(name=name,
                                                            description=description,
                                                            end_date=end_date,
                                                            status=status)
        self.save_dict()

    def handle_tasks_archive(self):
        tasks_archive = list(filter(lambda single: single.status == Status.DONE, self.tasks_by_id.values()))
        for index, single in enumerate(tasks_archive):
            print(f'Numer zadania: {index + 1}')
            print(print_task(single))
            print('')

    def menu(self):

        while True:
            try:
                choice = int(input('\n Wpisz odpowiednią cyfrę, aby wybrać akcję:\n'
                                   '1 - Dodaj nowe zadanie.\n'
                                   '2 - Zobacz aktywne zadania.\n'
                                   '3 - Archiwum zadań.\n'
                                   '4 - Wyjdź.\n'))

                if choice == 1:                             # add new task
                    self.handle_task_adding()

                elif choice == 2:                           # active tasks
                    self.handle_task_body()

                elif choice == 3:                           # tasks archive
                    self.handle_tasks_archive()

                elif choice == 4:                           # end program
                    break
            except KeyError:
                print('Nieprawidłowa komenda.\n')
            except ValueError:
                print('Nieprawidłowy format daty.\n')


if __name__ == '__main__':
    file_path = input('Podaj ścieżkę do pliku z zadaniami.\n')
    actions = TaskActions(file_path)
    actions.update_status()
    while actions.menu():
        pass


