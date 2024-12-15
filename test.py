import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.audio import SoundLoader
from kivmob import KivMob

# Set the window size to 540x960 and make it resizable
Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '750')
Config.set('graphics', 'resizable', '1')

class TestSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(TestSelectionScreen, self).__init__(**kwargs)
        self.load_tests()

    def load_tests(self):
        with open('tests_data.json', 'r') as f:
            self.tests_data = json.load(f)['tests']
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add background image
        background = Image(source='background.jpg', allow_stretch=True, keep_ratio=False)
        self.add_widget(background)
        
        # Create a scrollable list of tests
        scroll_view = ScrollView(size_hint=(1, 0.9))
        grid_layout = GridLayout(cols=1, padding=10, spacing=10, size_hint_y=None)
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        
        for test in self.tests_data:
            btn = Button(text=test['name'], size_hint_y=None, height=40, background_color=(1, 0, 0.8, 1))  # Pink color
            btn.bind(on_press=lambda instance, test=test: self.select_test(test))
            grid_layout.add_widget(btn)
        
        scroll_view.add_widget(grid_layout)
        layout.add_widget(scroll_view)
        
        # Add exit button at the bottom
        exit_button = Button(text="Exit", size_hint=(1, 0.1), background_color=(0.9, 0.9, 0.9, 1))  # Pink color
        exit_button.bind(on_press=self.exit_app)
        layout.add_widget(exit_button)
        
        self.add_widget(layout)

    def select_test(self, test):
        self.manager.current = 'test'
        self.manager.get_screen('test').load_test(test)

    def exit_app(self, instance):
        App.get_running_app().stop()

class TestScreen(Screen):
    def __init__(self, **kwargs):
        super(TestScreen, self).__init__(**kwargs)
        self.current_question_index = 0
        self.total_points = 0

        # Initialize KivMob with your AdMob App ID
        self.ads = KivMob("ca-app-pub-6453287851276572~6632728700")
        self.ads.new_banner("ca-app-pub-6453287851276572/6619420294", top_pos=False)
        self.ads.request_banner()
        self.ads.show_banner()


        # Load and play background music
        self.background_music = SoundLoader.load('sound/background.mp3')
        if self.background_music:
            self.background_music.loop = True
            self.background_music.play()

        # Load sound effects
        self.button_sound = SoundLoader.load('sound/button.mp3')
        self.result_sound = SoundLoader.load('sound/result.mp3')

    def load_test(self, test):
        self.test = test
        self.questions = test['questions']
        self.results = test['results']
        self.current_question_index = 0
        self.total_points = 0
        self.display_question()

    def display_question(self):
        self.clear_widgets()
        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            
            # Create a layout with a background color
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            with layout.canvas.before:
                Color(1, 0.75, 0.8, 1)  # Light grey color
                self.rect = Rectangle(size=layout.size, pos=layout.pos)
                layout.bind(size=self._update_rect, pos=self._update_rect)
            
            # Add question image if available
            if 'image' in question_data:
                question_image = Image(source=question_data['image'], size_hint_y=0.3, allow_stretch=True)
                layout.add_widget(question_image)
            
            question_label = Label(text=question_data['question'], size_hint_y=None, height=40)
            layout.add_widget(question_label)
            
            for answer in question_data['answers']:
                btn = Button(text=answer['text'], size_hint_y=None, height=40, background_color=(1, 0.75, 0.8, 1))  # Pink color
                btn.bind(on_press=lambda instance, points=answer['points']: self.answer_question(points))
                layout.add_widget(btn)
            
            self.add_widget(layout)
        else:
            self.display_result()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def answer_question(self, points):
        self.total_points += points
        self.current_question_index += 1

        # Play button sound effect
        if self.button_sound:
            self.button_sound.play()

        self.display_question()

    def display_result(self):
        self.clear_widgets()
        result_text = "No result found"
        for result in self.results:
            if result['min_points'] <= self.total_points <= result['max_points']:
                result_text = result['result']
                break
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        with layout.canvas.before:
            Color(1, 0.75, 0.8, 1)  # Light grey color
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self._update_rect, pos=self._update_rect)
        
        result_label = Label(text=f"Your result: {result_text}", size_hint_y=None, height=40)
        layout.add_widget(result_label)
        back_button = Button(text="Back to Main Menu", size_hint_y=None, height=40, background_color=(1, 0.75, 0.8, 1))  # Pink color
        back_button.bind(on_press=self.go_back_to_main_menu)
        layout.add_widget(back_button)
        self.add_widget(layout)

        # Play result sound effect
        if self.result_sound:
            self.result_sound.play()

    def go_back_to_main_menu(self, instance):
        self.manager.current = 'test_selection'

class TestApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TestSelectionScreen(name='test_selection'))
        sm.add_widget(TestScreen(name='test'))
        return sm

if __name__ == '__main__':
    TestApp().run()