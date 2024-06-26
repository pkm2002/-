import sqlite3
import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.metrics import dp  # Импорт функции dp для конвертации в пиксели DP



Window.clearcolor = (0.05, 0.05, 0.2, 1)


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=10)

        self.user_login = TextInput(hint_text='Login', multiline=False, size_hint=(None, None), size=(5*37.7952755906, 1*37.7952755906),
                                    background_color=(1, 1, 1, 1),  # белый фон
                                    foreground_color=(0, 0, 0, 1),  # черный текст
                                    font_size=15,  # размер шрифта
                                    padding=(10, 10),  # отступы вокруг текста
                                   # border=(1, 1, 1, 1)  # цвет рамки
                                    )
        self.user_pass = TextInput(hint_text='Password', password=True, multiline=False, size_hint=(None, None), size=(5*37.7952755906, 1*37.7952755906))
        self.btn_register = Button(text='Register', size_hint_y=None, height=50, background_color=(0.2, 0.4, 0.6, 1),  size_hint=(None, None), size=(5*37.7952755906, 1*37.7952755906))
        self.btn_auth = Button(text='Login', size_hint_y=None, height=50, background_color=(0.2, 0.4, 0.6, 1),  size_hint=(None, None), size=(5*37.7952755906, 1*37.7952755906))
        self.error_label = Label(text='', color=(1, 0, 0, 1),  size=(5*37.7952755906, 3*37.7952755906))  # Red text for errors

        layout.add_widget(Label(text='Регистрация и Авторизация', size_hint_y=None, height=50, color=(1, 1, 1, 1)))
        layout.add_widget(self.user_login)
        layout.add_widget(self.user_pass)
        layout.add_widget(self.btn_register)
        layout.add_widget(self.btn_auth)
        layout.add_widget(self.error_label)

        self.btn_register.bind(on_press=self.register)
        self.btn_auth.bind(on_press=self.auth_user)

        self.add_widget(layout)
        self.create_db()

    def create_db(self):
        db = sqlite3.connect('Baza')
        cur = db.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            login TEXT,
            pass TEXT
        )""")
        db.close()

    def register(self, instance):
        db = sqlite3.connect('Baza')
        cur = db.cursor()
        cur.execute("INSERT INTO users (login, pass) VALUES (?, ?)", (self.user_login.text, self.user_pass.text))
        db.commit()
        db.close()
        self.user_login.text = ''
        self.user_pass.text = ''
        self.btn_register.text = 'Добавлено'

    def auth_user(self, instance):
        db = sqlite3.connect('Baza')
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE login = ? AND pass = ?", (self.user_login.text, self.user_pass.text))
        if cur.fetchone():
            if self.user_login.text and self.user_pass.text:
                self.manager.current = 'main'
                self.error_label.text = ''
            else:
                self.error_label.text = 'Заполните логин и пароль!'
        else:
            self.error_label.text = 'Неверно введенные данные!'
        db.close()

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.group_selection_button = Button(text='Выбрать по группе', size_hint=(None, None), size=(dp(150), dp(30)), background_color=(0.3, 0.5, 0.7, 1))
        self.group_selection_button.bind(on_press=self.show_group_selection)
        self.layout.add_widget(self.group_selection_button)

        self.fio_selection_button = Button(text='Выбрать по ФИО', size_hint=(None, None), size=(dp(150), dp(30)), background_color=(0.3, 0.5, 0.7, 1))
        self.fio_selection_button.bind(on_press=self.show_fio_selection)
        self.layout.add_widget(self.fio_selection_button)

        self.back_button = Button(text='Вернуться к выбору',  size_hint_y=None, height=50,  background_color=(0.2, 0.4, 0.6, 1))


      #  self.back_button = Button(text='Вернуться к выбору', size_hint_y=None, height=30, background_color=(0.2, 0.4, 0.6, 1),size=(5*37.7952755906, 1*37.7952755906))
        self.back_button.bind(on_press=self.show_initial_buttons)

        self.clear_button = Button(text='Очистить', size_hint_y=None, height=50,  background_color=(0.2, 0.4, 0.6, 1))
        self.clear_button.bind(on_press=self.clear_fields)

        self.group_dropdown = DropDown()
        self.group_dropdown.bind(on_select=self.update_student_dropdown)
        self.group_button = Button(text='Выбрать группу', size_hint_y=None, height=50,  background_color=(0.3, 0.5, 0.7, 1))
        self.group_button.bind(on_release=self.show_group_dropdown)

        self.student_dropdown = DropDown()
        self.student_button = Button(text='Выбрать студента',size_hint_y=None, height=50,  background_color=(0.3, 0.5, 0.7, 1))
        self.student_button.bind(on_release=self.student_dropdown.open)

        self.search_input = TextInput(hint_text='Поиск по ФИО', multiline=False, size_hint_y=None, height=50)
        self.search_input.bind(text=self.filter_dropdown)

        self.info_button = Button(text='Выбрать', size_hint_y=None, height=50, background_color=(0.2, 0.4, 0.6, 1))
        self.info_button.bind(on_release=self.show_info_dropdown)

        self.info_dropdown = DropDown()
        info_data = self.load_info_data()
        for item in info_data:
            btn = Button(text=str(item), size_hint_y=None, height=50, background_color=(0.5, 0.5, 0.5, 1))
            btn.bind(on_release=lambda btn: self.info_dropdown.select(btn.text))
            self.info_dropdown.add_widget(btn)
        self.info_dropdown.bind(on_select=lambda instance, x: setattr(self.info_button, 'text', x))

        self.elements_button = Button(text='Выбрать элементы', size_hint_y=None, height=50, background_color=(0.3, 0.5, 0.7, 1))
        self.elements_button.bind(on_release=self.show_elements_dropdown)
        self.elements_dropdown = DropDown()
        elements_data = self.load_elements_data()
        for item in elements_data:
            btn = Button(text=str(item), size_hint_y=None, height=50, background_color=(0.5, 0.5, 0.5, 1))
            btn.bind(on_release=lambda btn: self.elements_dropdown.select(btn.text))
            self.elements_dropdown.add_widget(btn)
        self.elements_dropdown.bind(on_select=lambda instance, x: setattr(self.elements_button, 'text', x))

        self.letter_input = TextInput(hint_text='Введите номер '
                                                'буквы', multiline=False, size_hint_y=None, height=50)
        self.process_button = Button(text='Сгенерировать результат',  size_hint_y=None, height=50,  background_color=(0.2, 0.4, 0.6, 1))
        self.process_button.bind(on_press=self.process_input)
        self.result_label = Label(text='Результат:', size_hint_y=None, height=50, color=(1, 1, 1, 1))

        self.add_widget(self.layout)

    def show_group_selection(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(self.back_button)
        self.layout.add_widget(self.clear_button)
        self.layout.add_widget(self.group_button)
        self.layout.add_widget(self.student_button)
        self.layout.add_widget(self.elements_button)
        self.layout.add_widget(self.letter_input)
        self.layout.add_widget(self.process_button)
        self.layout.add_widget(self.result_label)

    def show_fio_selection(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(self.back_button)
        self.layout.add_widget(self.clear_button)
        self.layout.add_widget(self.search_input)
        self.layout.add_widget(self.info_button)
        self.layout.add_widget(self.elements_button)
        self.layout.add_widget(self.letter_input)
        self.layout.add_widget(self.process_button)
        self.layout.add_widget(self.result_label)

    def show_initial_buttons(self, instance):
        self.layout.clear_widgets()
        self.layout.add_widget(self.group_selection_button)
        self.layout.add_widget(self.fio_selection_button)

    def clear_fields(self, instance):
        self.group_button.text = 'Выбрать группу'
        self.student_button.text = 'Выбрать студента'
        self.search_input.text = ''
        self.info_button.text = 'Выбрать'
        self.elements_button.text = 'Выбрать элементы'
        self.letter_input.text = ''
        self.result_label.text = 'Результат:'

    def show_elements_dropdown(self, instance):
        self.elements_dropdown.open(instance)

    def show_info_dropdown(self, instance):
        self.info_dropdown.open(instance)

    def filter_dropdown(self, instance, value):
        first_letter = value[0] if value else ''
        filtered_items = [item for item in self.load_info_data() if item.startswith(first_letter)]
        self.info_dropdown.clear_widgets()
        for item in filtered_items:
            btn = Button(text=str(item), size_hint_y=None, height=50, background_color=(0.5, 0.5, 0.5, 1))
            btn.bind(on_release=lambda btn: self.info_dropdown.select(btn.text))
            self.info_dropdown.add_widget(btn)

    def process_input(self, instance):
        try:
            A = [int(x) for x in self.elements_button.text.split(',')]  # Обработка ввода массива данных
            k = len(A)  # Размер массива данных A вычисляется автоматически
            s = self.info_button.text
            p = int(self.letter_input.text)

            str_ru = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
            C = [0] * 3
            h = 0

            def calculate_average(mas, k, l):
                avg = sum(mas[k:l]) / len(mas[k:l])
                return round(avg)

            for n1 in range(p - 1, len(s)):
                n = s[n1]
                if h == 3:
                    break
                num = str_ru.index(n) // 2 + 1
                C[h] = num
                mod = C[h]
                if C[h] > k:
                    if C[h] % k == 0:
                        mod = 0
                    else:
                        mod = C[h] % k
                avg_val = calculate_average(A, 0, mod)
                A[mod - 1] = avg_val
                h += 1
            self.result_label.text = f'Результат: {A}'
        except Exception as e:
            self.result_label.text = f'Ошибка: {e}'

    def load_elements_data(self):
        try:
            df = pd.read_excel('1.xls')  # Замените '1.xls' на путь к вашему файлу
            return df['task'].tolist()  # Замените 'Название' на название столбца в вашем файле
        except Exception as e:
            print("Ошибка при загрузке данных из файла 1.xls:", e)
            return []

    def load_info_data(self):
        try:
            df = pd.read_excel('ef2024.xls')  # Замените 'ef2024.xls' на путь к вашему файлу
            return df['Студент'].tolist()  # Замените 'Студент' на название столбца в вашем файле
        except Exception as e:
            print("Ошибка при загрузке данных из файла ef2024.xls:", e)
            return []

    def update_student_dropdown(self, instance, x):
        selected_group = x
        students = self.get_students_by_group(selected_group)
        self.student_dropdown.clear_widgets()
        for student in students:
            btn = Button(text=str(student), size_hint_y=None, height=50, background_color=(0.5, 0.5, 0.5, 1))
            btn.bind(on_release=lambda btn: self.student_dropdown.select(btn.text))
            self.student_dropdown.add_widget(btn)
        self.student_dropdown.bind(on_select=lambda instance, x: setattr(self.student_button, 'text', x))

    def get_students_by_group(self, group_number):
        try:
            df = pd.read_excel('student.xls')
            filtered_students = df[df['Группа'] == group_number]['ФИО'].tolist()
            return filtered_students
        except Exception as e:
            print("Ошибка при загрузке данных из файла students.xlsx:", e)
            return []

    def show_group_dropdown(self, instance):
        self.group_dropdown.clear_widgets()
        groups = self.load_groups_data()
        for group in groups:
            btn = Button(text=str(group), size_hint_y=None, height=50, background_color=(0.5, 0.5, 0.5, 1))
            btn.bind(on_release=lambda btn: self.group_dropdown.select(btn.text))
            self.group_dropdown.add_widget(btn)
        self.group_dropdown.open(instance)

    def load_groups_data(self):
        try:
            df = pd.read_excel('student.xls')
            return df['Группа'].unique().tolist()
        except Exception as e:
            print("Ошибка при загрузке данных из файла students.xlsx:", e)
            return []

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    MyApp().run()
