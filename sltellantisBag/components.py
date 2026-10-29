import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle, StencilPush, StencilUse, StencilUnUse, StencilPop
from database import obter_perfil_atual, salvar_dados_gerais


def abrir_seletor_foto(callback_atualizar):
    content = BoxLayout(orientation='vertical', spacing=10, padding=10)
    filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg', '*.gif'])
    content.add_widget(filechooser)

    btn_layout = BoxLayout(size_hint_y=None, height='45dp', spacing=10)
    btn_cancelar = Button(text='Cancelar', background_color=(0.7, 0.2, 0.2, 1), color=(1, 1, 1, 1), bold=True)
    btn_escolher = Button(text='Selecionar Mídia', background_color=(1.0, 0.82, 0.0, 1), color=(0.12, 0.14, 0.18, 1),
                          bold=True)

    popup = Popup(title='Escolher GIF/Foto de Perfil', content=content, size_hint=(0.9, 0.9))

    def selecionar(instance):
        selection = filechooser.selection
        if selection:
            perfil = obter_perfil_atual()
            perfil["foto_path"] = selection[0]
            salvar_dados_gerais()
            callback_atualizar()
            popup.dismiss()

    btn_escolher.bind(on_release=selecionar)
    btn_cancelar.bind(on_release=popup.dismiss)
    btn_layout.add_widget(btn_cancelar)
    btn_layout.add_widget(btn_escolher)
    content.add_widget(btn_layout)
    popup.open()


class CircularAvatar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = ('90dp', '90dp')

        with self.canvas.before:
            Color(1.0, 0.82, 0.0, 1)
            self.bg_circle = Ellipse(size=self.size, pos=self.pos)
            StencilPush()
            self.stencil_ellipse = Ellipse(size=(self.size[0] - 6, self.size[1] - 6),
                                           pos=(self.pos[0] + 3, self.pos[1] + 3))
            StencilUse()

        self.bind(size=self._update_graphics, pos=self._update_graphics)
        self.img_widget = None
        self.lbl_widget = Label(text='GIF', font_size='12sp', bold=True, color=(0.12, 0.14, 0.18, 1), halign='center',
                                valign='middle')
        self.lbl_widget.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.add_widget(self.lbl_widget)

        with self.canvas.after:
            StencilUnUse()
            StencilPop()

    def atualizar_imagem(self, path_foto):
        self.clear_widgets()
        if not path_foto or not os.path.exists(path_foto):
            path_padrao = os.path.join('icones', 'carregamento.1.gif')
            if os.path.exists(path_padrao):
                path_foto = path_padrao

        if path_foto and os.path.exists(path_foto):
            self.img_widget = Image(source=path_foto, allow_stretch=True, keep_ratio=False, size=self.size)
            self.add_widget(self.img_widget)
        else:
            self.add_widget(self.lbl_widget)

    def _update_graphics(self, instance, value):
        self.bg_circle.size = instance.size
        self.bg_circle.pos = instance.pos
        self.stencil_ellipse.size = (instance.size[0] - 6, instance.size[1] - 6)
        self.stencil_ellipse.pos = (instance.pos[0] + 3, instance.pos[1] + 3)


class RoundedButton(Button):
    def __init__(self, bg_color=(0.2, 0.6, 0.4, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])


class CriarBarraNavegacao(BoxLayout):
    def __init__(self, ativa='producao', **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = '55dp'
        self.orientation = 'horizontal'

        with self.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        botoes = [
            ('Início', 'inicio'),
            ('Relat.', 'relatorios'),
            ('Produção', 'producao'),
            ('Config.', 'config'),
            ('Suporte', 'suporte')
        ]

        for texto, tela in botoes:
            cor_texto = (1.0, 0.82, 0.0, 1) if tela == ativa else (0.8, 0.8, 0.8, 1)
            btn = Button(
                text=texto,
                background_color=(0, 0, 0, 0),
                color=cor_texto,
                bold=True,
                font_size='12sp'
            )
            btn.bind(on_release=lambda inst, t=tela: self.mudar_tela(t))
            self.add_widget(btn)

    def mudar_tela(self, nome_tela):
        from kivy.app import App
        app = App.get_running_app()
        if app.sm.current != nome_tela:
            app.sm.current = nome_tela

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos