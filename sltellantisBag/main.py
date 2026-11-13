from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens import (
    WelcomeScreen, HomeScreen, ReportsScreen, ProductionScreen,
    SupportScreen, ConfigScreen, ThemeScreen, UserProfileScreen,
    ChecagemScreen,
)

class MyBagApp(App):
    def build(self):
        self.title = 'MyBag - Sistema de Produção'
        self.sm = ScreenManager()

        # 1. Adicionamos todas as telas primeiro
        self.sm.add_widget(WelcomeScreen(name='welcome'))
        self.sm.add_widget(HomeScreen(name='inicio'))
        self.sm.add_widget(ReportsScreen(name='relatorios'))
        self.sm.add_widget(ProductionScreen(name='producao'))
        self.sm.add_widget(ConfigScreen(name='config'))
        self.sm.add_widget(ThemeScreen(name='theme'))
        self.sm.add_widget(SupportScreen(name='suporte'))
        self.sm.add_widget(UserProfileScreen(name='userprofile'))
        self.sm.add_widget(ChecagemScreen(name='checagem'))

        # 2. Definimos a tela inicial por último com segurança
        self.sm.current = 'welcome'

        return self.sm

if __name__ == '__main__':
    MyBagApp().run()