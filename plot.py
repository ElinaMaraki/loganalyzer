from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class PhoneAppUI(BoxLayout):
    def __init__(self, **kwargs):
        super(PhoneAppUI, self).__init__(**kwargs)

        self.orientation = "vertical"

        self.label = Button(text="Phone Application", size_hint=(1, 0.2))
        self.add_widget(self.label)

        self.dial_button = Button(text="Dial", size_hint=(1, 0.2))
        self.dial_button.bind(on_press=self.dial)
        self.add_widget(self.dial_button)

        self.call_log_button = Button(text="Call Log", size_hint=(1, 0.2))
        self.call_log_button.bind(on_press=self.show_call_log)
        self.add_widget(self.call_log_button)

        self.exit_button = Button(text="Exit", size_hint=(1, 0.2))
        self.exit_button.bind(on_press=self.exit_app)
        self.add_widget(self.exit_button)

    def dial(self, instance):
        # Functionality for dialing a number
        print("Dialing...")

    def show_call_log(self, instance):
        # Functionality for displaying call log
        print("Call Log")

    def exit_app(self, instance):
        # Exit the application
        App.get_running_app().stop()


class PhoneApp(App):
    def build(self):
        return PhoneAppUI()


if __name__ == "__main__":
    PhoneApp().run()
