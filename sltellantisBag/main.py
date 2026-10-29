from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens import WelcomeScreen, HomeScreen, ReportsScreen, ProductionScreen, SupportScreen, TasksScreen

class MyBagApp(App):
    def build(self):
        self.title = 'MyBag - Sistema de Produção'
        self.sm = ScreenManager()

        self.sm.add_widget(WelcomeScreen(name='welcome'))
        self.sm.add_widget(HomeScreen(name='inicio'))
        self.sm.add_widget(ReportsScreen(name='relatorios'))
        self.sm.add_widget(ProductionScreen(name='producao'))
        self.sm.add_widget(TasksScreen(name='config'))       # Abre a tela de QR Code ao clicar em config
        self.sm.add_widget(SupportScreen(name='suporte'))     # Abre a tela de suporte com o seu contato

        self.sm.current = 'welcome'
        return self.sm

if __name__ == '__main__':
    MyBagApp().run()