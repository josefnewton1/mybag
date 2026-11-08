from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens import WelcomeScreen, HomeScreen, ReportsScreen, ProductionScreen,  TasksScreen, SupportScreen, ConfigScreen, ThemeScreen, UserProfileScreen, ChecagemScreen

class MyBagApp(App):
    def build(self):
        self.title = 'MyBag - Sistema de Produção'
        self.sm = ScreenManager()

        self.sm.add_widget(WelcomeScreen(name='welcome'))
        self.sm.add_widget(HomeScreen(name='inicio'))
        self.sm.add_widget(ReportsScreen(name='relatorios'))
        self.sm.add_widget(ProductionScreen(name='producao'))
        self.sm.add_widget(ConfigScreen(name='config'))
        self.sm.add_widget(ThemeScreen(name='theme_screen'))  # <--- ESTA LINHA FALTAVA NO SEU MAIN.PY
        self.sm.add_widget(SupportScreen(name='suporte'))
        self.sm.add_widget(UserProfileScreen(name='user_profile'))
        self.sm.current = 'welcome'
        self.sm.add_widget(ChecagemScreen(name='checagem'))
        return self.sm

if __name__ == '__main__':
    MyBagApp().run()