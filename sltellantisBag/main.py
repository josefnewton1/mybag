import json
import os
import csv
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, StencilPush, StencilUse, StencilUnUse, StencilPop
from datetime import datetime
from kivy.core.clipboard import Clipboard

try:
    from plyer import share

    has_plyer = True
except ImportError:
    has_plyer = False

CONFIG_FILE = "mybag_usuarios_config.json"


def carregar_dados_gerais():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "usuario_atual": "José Nilton",
        "perfis": {
            "José Nilton": {
                "foto_path": "",
                "historico_salvo": [],
                "total_produzido_hoje": 0,
                "meta_hoje": 720,
                "porcentagem_hoje": 0.0,
                "oee_semana": 0.0,
                "meta_mes_pct": 0.0
            }
        }
    }


def salvar_dados_gerais():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DADOS_APP, f, ensure_ascii=False, indent=4)
        gerar_planilha_csv()
    except Exception as e:
        print("Erro ao salvar dados:", e)


def gerar_planilha_csv():
    try:
        with open("mybag_banco_dados.csv", mode="w", newline="", encoding="utf-8-sig") as arquivo_csv:
            campos = [
                "Nome do Usuário", "Caminho da Foto", "Meta Diária",
                "Total Produzido Hoje", "Porcentagem Concluída Hoje (%)",
                "OEE da Semana (%)", "Produção do Mês (%)", "Histórico de Relatórios Salvos"
            ]
            escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
            escritor.writeheader()

            for nome_usuario, perfil in DADOS_APP["perfis"].items():
                historico_str = " | ".join(perfil["historico_salvo"]) if perfil[
                    "historico_salvo"] else "Nenhum histórico"
                escritor.writerow({
                    "Nome do Usuário": nome_usuario,
                    "Caminho da Foto": perfil.get("foto_path", ""),
                    "Meta Diária": perfil.get("meta_hoje", 720),
                    "Total Produzido Hoje": perfil.get("total_produzido_hoje", 0),
                    "Porcentagem Concluída Hoje (%)": perfil.get("porcentagem_hoje", 0.0),
                    "OEE da Semana (%)": perfil.get("oee_semana", 0.0),
                    "Produção do Mês (%)": perfil.get("meta_mes_pct", 0.0),
                    "Histórico de Relatórios Salvos": historico_str
                })
    except Exception as e:
        print("Erro ao gerar planilha CSV:", e)


DADOS_APP = carregar_dados_gerais()
gerar_planilha_csv()


def obter_perfil_atual():
    nome = DADOS_APP["usuario_atual"]
    if nome not in DADOS_APP["perfis"]:
        DADOS_APP["perfis"][nome] = {
            "foto_path": "",
            "historico_salvo": [],
            "total_produzido_hoje": 0,
            "meta_hoje": 720,
            "porcentagem_hoje": 0.0,
            "oee_semana": 0.0,
            "meta_mes_pct": 0.0
        }
    return DADOS_APP["perfis"][nome]


# ==========================================
# SELETOR DE FOTO / GIF
# ==========================================
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


# ==========================================
# WIDGET DE FOTO / GIF DE PERFIL CIRCULAR
# ==========================================
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


# ==========================================
# BOTÃO CUSTOMIZADO ARREDONDADO
# ==========================================
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


# ==========================================
# 0. TELA DE BOAS-VINDAS
# ==========================================
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        with main_layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)

        main_layout.add_widget(Label(size_hint_y=None, height='10dp'))

        container_logo = BoxLayout(size_hint=(None, None), size=('190dp', '135dp'), pos_hint={'center_x': 0.5})
        path_gif = os.path.join('icones', 'carregamento.1.gif')
        if os.path.exists(path_gif):
            img_logo = Image(source=path_gif, allow_stretch=True, keep_ratio=True)
        else:
            path_logo_png = os.path.join('icones', 'logo_mybag.png')
            if os.path.exists(path_logo_png):
                img_logo = Image(source=path_logo_png, allow_stretch=True, keep_ratio=True)
            else:
                img_logo = Label(text='[Coloque carregamento.1.gif\nna pasta icones]', color=(0.12, 0.14, 0.18, 1),
                                 halign='center')
        container_logo.add_widget(img_logo)
        main_layout.add_widget(container_logo)

        container_avatar = BoxLayout(orientation='vertical', size_hint=(None, None), size=('85dp', '85dp'),
                                     pos_hint={'center_x': 0.5})
        self.avatar_real = CircularAvatar(size=('85dp', '85dp'))
        container_avatar.add_widget(self.avatar_real)
        main_layout.add_widget(container_avatar)

        btn_trocar = Button(
            text='Alterar GIF de Perfil',
            size_hint=(None, None),
            size=('160dp', '30dp'),
            pos_hint={'center_x': 0.5},
            background_color=(0.12, 0.14, 0.18, 1),
            color=(1.0, 0.82, 0.0, 1),
            bold=True,
            font_size='11sp'
        )
        btn_trocar.bind(on_release=lambda x: abrir_seletor_foto(self.carregar_foto_usuario))
        main_layout.add_widget(btn_trocar)

        box_input = BoxLayout(orientation='vertical', size_hint_y=None, height='75dp', spacing=5)
        lbl_instrucao = Label(text='Seu Nome Completo (Usuário):', color=(0.12, 0.14, 0.18, 1), font_size='12sp',
                              bold=True, halign='left')
        lbl_instrucao.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.input_nome = TextInput(
            text=DADOS_APP["usuario_atual"],
            multiline=False,
            font_size='14sp',
            size_hint_y=None,
            height='38dp',
            halign='center'
        )
        self.input_nome.bind(text=self.ao_mudar_nome)
        box_input.add_widget(lbl_instrucao)
        box_input.add_widget(self.input_nome)
        main_layout.add_widget(box_input)

        btn_entrar = Button(
            text='ENTRAR NO SISTEMA',
            size_hint_y=None,
            height='48dp',
            background_color=(1.0, 0.82, 0.0, 1),
            color=(0.12, 0.14, 0.18, 1),
            bold=True,
            font_size='15sp'
        )
        btn_entrar.bind(on_release=self.ir_para_inicio)
        main_layout.add_widget(btn_entrar)
        main_layout.add_widget(Label())

        self.add_widget(main_layout)
        self.carregar_foto_usuario()

    def ao_mudar_nome(self, instance, valor):
        nome_limpo = valor.strip()
        if nome_limpo:
            DADOS_APP["usuario_atual"] = nome_limpo
            obter_perfil_atual()
            self.carregar_foto_usuario()

    def carregar_foto_usuario(self):
        perfil = obter_perfil_atual()
        self.avatar_real.atualizar_imagem(perfil["foto_path"])

    def ir_para_inicio(self, instance):
        nome_digitado = self.input_nome.text.strip()
        if nome_digitado:
            DADOS_APP["usuario_atual"] = nome_digitado
            obter_perfil_atual()
            salvar_dados_gerais()

        app = App.get_running_app()
        home_screen = app.sm.get_screen('inicio')
        home_screen.atualizar_dados_dashboard()

        app.sm.current = 'inicio'

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# 1. TELA DE INÍCIO (PAINEL DE CONTROLE)
# ==========================================
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = BoxLayout(orientation='vertical')

        with self.main_layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.size)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

        lbl_title = Label(text='PAINEL DE CONTROLE - MYBAG', color=(1.0, 0.82, 0.0, 1), font_size='16sp', bold=True,
                          halign='center')
        header.add_widget(lbl_title)
        self.main_layout.add_widget(header)

        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=14, padding=14)
        self.content.bind(minimum_height=self.content.setter('height'))

        data_atual = datetime.now().strftime('%A, %d de %B, %Y')
        lbl_data = Label(text=f'Hoje: {data_atual}', color=(0.4, 0.3, 0.2, 1), font_size='12sp', bold=True,
                         size_hint_y=None, height='22dp', halign='center')
        lbl_data.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.content.add_widget(lbl_data)

        card_perfil = BoxLayout(orientation='horizontal', size_hint_y=None, height='95dp', padding=12, spacing=15)
        with card_perfil.canvas.before:
            Color(1, 1, 1, 1)
            self.p_bg = RoundedRectangle(size=card_perfil.size, pos=card_perfil.pos, radius=[14])
        card_perfil.bind(size=lambda inst, val: setattr(self.p_bg, 'size', inst.size),
                         pos=lambda inst, val: setattr(self.p_bg, 'pos', inst.pos))

        self.avatar_perfil = CircularAvatar(size=('75dp', '75dp'))
        box_avatar_wrapper = BoxLayout(size_hint_x=None, width='75dp')
        box_avatar_wrapper.add_widget(self.avatar_perfil)
        card_perfil.add_widget(box_avatar_wrapper)

        box_user_info = BoxLayout(orientation='vertical', spacing=4, padding=[10, 10, 0, 0])
        self.lbl_nome = Label(text='Bom dia!', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='16sp', halign='left',
                              valign='middle')
        self.lbl_nome.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        lbl_cargo = Label(text='Multiplicador - 2° Turno', color=(0.5, 0.4, 0.3, 1), font_size='13sp', halign='left',
                          valign='middle')
        lbl_cargo.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        box_user_info.add_widget(self.lbl_nome)
        box_user_info.add_widget(lbl_cargo)
        card_perfil.add_widget(box_user_info)
        self.content.add_widget(card_perfil)

        card_prod = BoxLayout(orientation='vertical', size_hint_y=None, height='105dp', padding=12, spacing=6)
        with card_prod.canvas.before:
            Color(1, 1, 1, 1)
            self.prod_bg = RoundedRectangle(size=card_prod.size, pos=card_prod.pos, radius=[14])
        card_prod.bind(size=lambda inst, val: setattr(self.prod_bg, 'size', inst.size),
                       pos=lambda inst, val: setattr(self.prod_bg, 'pos', inst.pos))

        lbl_prod_title = Label(text='PRODUÇÃO TOTAL DO DIA', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='12sp',
                               halign='center')
        lbl_prod_title.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.lbl_prod_val = Label(text='0 UNIDADES PRODUZIDAS / META 720', color=(0.7, 0.5, 0.0, 1), bold=True,
                                  font_size='13sp', halign='center')
        self.lbl_prod_val.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.lbl_prod_pct = Label(text='0.0% Concluído ❌', color=(0.8, 0.2, 0.2, 1), font_size='12sp', halign='center')
        self.lbl_prod_pct.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        card_prod.add_widget(lbl_prod_title)
        card_prod.add_widget(self.lbl_prod_val)
        card_prod.add_widget(self.lbl_prod_pct)
        self.content.add_widget(card_prod)

        box_ope = BoxLayout(orientation='horizontal', size_hint_y=None, height='95dp', spacing=12)

        card_ope1 = BoxLayout(orientation='vertical', padding=10, spacing=4)
        with card_ope1.canvas.before:
            Color(1, 1, 1, 1)
            self.o1_bg = RoundedRectangle(size=card_ope1.size, pos=card_ope1.pos, radius=[14])
        card_ope1.bind(size=lambda inst, val: setattr(self.o1_bg, 'size', inst.size),
                       pos=lambda inst, val: setattr(self.o1_bg, 'pos', inst.pos))

        lbl_oee_title = Label(text='OEE (SEMANA)', color=(0.4, 0.3, 0.2, 1), font_size='11sp', bold=True,
                              halign='center')
        lbl_oee_title.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.lbl_oee_val = Label(text='0%', color=(0.12, 0.14, 0.18, 1), font_size='22sp', bold=True, halign='center')
        self.lbl_oee_val.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        card_ope1.add_widget(lbl_oee_title)
        card_ope1.add_widget(self.lbl_oee_val)

        card_ope2 = BoxLayout(orientation='vertical', padding=10, spacing=4)
        with card_ope2.canvas.before:
            Color(1, 1, 1, 1)
            self.o2_bg = RoundedRectangle(size=card_ope2.size, pos=card_ope2.pos, radius=[14])
        card_ope2.bind(size=lambda inst, val: setattr(self.o2_bg, 'size', inst.size),
                       pos=lambda inst, val: setattr(self.o2_bg, 'pos', inst.pos))

        lbl_mes_title = Label(text='PRODUÇÃO DO MÊS', color=(0.4, 0.3, 0.2, 1), font_size='11sp', bold=True,
                              halign='center')
        lbl_mes_title.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.lbl_mes_val = Label(text='0%', color=(0.12, 0.14, 0.18, 1), font_size='22sp', bold=True, halign='center')
        self.lbl_mes_val.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        card_ope2.add_widget(lbl_mes_title)
        card_ope2.add_widget(self.lbl_mes_val)

        box_ope.add_widget(card_ope1)
        box_ope.add_widget(card_ope2)
        self.content.add_widget(box_ope)

        lbl_acoes = Label(text='AÇÕES RÁPIDAS', color=(0.4, 0.3, 0.2, 1), font_size='12sp', bold=True, size_hint_y=None,
                          height='24dp', halign='left')
        lbl_acoes.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.content.add_widget(lbl_acoes)

        btn_ir_producao = Button(
            text='+ REGISTRAR PRODUÇÃO',
            size_hint_y=None,
            height='50dp',
            background_color=(1.0, 0.82, 0.0, 1),
            color=(0.12, 0.14, 0.18, 1),
            bold=True,
            font_size='14sp'
        )
        btn_ir_producao.bind(on_release=self.ir_para_registrar_producao)
        self.content.add_widget(btn_ir_producao)

        scroll.add_widget(self.content)
        self.main_layout.add_widget(scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='inicio'))
        self.add_widget(self.main_layout)

    def on_enter(self):
        self.atualizar_dados_dashboard()

    def atualizar_dados_dashboard(self):
        perfil = obter_perfil_atual()
        self.lbl_nome.text = f'Bom dia, {DADOS_APP["usuario_atual"]}!'

        self.avatar_perfil.atualizar_imagem(perfil["foto_path"])

        total = perfil["total_produzido_hoje"]
        meta = perfil["meta_hoje"]
        pct = perfil["porcentagem_hoje"]

        self.lbl_prod_val.text = f'{total} UNIDADES PRODUZIDAS / META {meta}'
        emoji = "🟢" if pct >= 100 else "⚠️" if pct >= 80 else "❌"
        self.lbl_prod_pct.text = f'{pct:.1f}% Concluído {emoji}'

        self.lbl_oee_val.text = f'{perfil["oee_semana"]:.1f}%'
        self.lbl_mes_val.text = f'{perfil["meta_mes_pct"]:.1f}%'

    def ir_para_registrar_producao(self, instance):
        app = App.get_running_app()
        prod_screen = app.sm.get_screen('producao')
        prod_screen.limpar_campos()
        app.sm.current = 'producao'

    def mudar_tela(self, nome_tela):
        self.manager.current = nome_tela

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# 2. TELA DE RELATÓRIOS
# ==========================================
class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')

        with self.main_layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.size)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))
        header.add_widget(Label(text='RELATÓRIOS SALVOS', color=(1.0, 0.82, 0.0, 1), font_size='17sp', bold=True))
        self.main_layout.add_widget(header)

        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=12)
        self.content.bind(minimum_height=self.content.setter('height'))

        self.scroll.add_widget(self.content)
        self.main_layout.add_widget(self.scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='relatorios'))
        self.add_widget(self.main_layout)

    def on_enter(self):
        self.content.clear_widgets()
        perfil = obter_perfil_atual()
        if not perfil["historico_salvo"]:
            self.content.add_widget(
                Label(text=f'Nenhum relatório para {DADOS_APP["usuario_atual"]}.', color=(0.4, 0.3, 0.2, 1),
                      font_size='13sp', size_hint_y=None, height='40dp'))
        else:
            for i, rel in enumerate(perfil["historico_salvo"], 1):
                card_rel = BoxLayout(orientation='vertical', size_hint_y=None, height='160dp', padding=12)
                with card_rel.canvas.before:
                    Color(1, 1, 1, 1)
                    RoundedRectangle(size=card_rel.size, pos=card_rel.pos, radius=[10])

                lbl_rel = Label(
                    text=f"--- Relatório #{i} ---\n{rel}",
                    color=(0.12, 0.14, 0.18, 1),
                    font_size='11sp',
                    halign='left',
                    valign='top'
                )
                lbl_rel.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
                card_rel.add_widget(lbl_rel)
                self.content.add_widget(card_rel)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# 3. TELA DE PRODUÇÃO
# ==========================================
class ProductionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical')

        with main_layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.size)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))
        header.add_widget(
            Label(text='ACOMPANHAMENTO DE PRODUÇÃO', color=(1.0, 0.82, 0.0, 1), font_size='17sp', bold=True))
        main_layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12, padding=12)
        content.bind(minimum_height=content.setter('height'))

        # Card de Seleção de Meta limpo e integrado no fundo bege
        box_meta_card = BoxLayout(orientation='vertical', size_hint_y=None, height='95dp', padding=8, spacing=6)
        lbl_meta_tit = Label(text='DEFINIÇÃO DE META (720 ou 360)', color=(0.12, 0.14, 0.18, 1), font_size='13sp',
                             bold=True)
        self.input_meta_selecionada = TextInput(text='720', multiline=False, font_size='15sp', size_hint_y=None,
                                                height='35dp', halign='center')

        btn_salvar_meta = RoundedButton(text='Salvar Meta', bg_color=(0.85, 0.65, 0.1, 1), size_hint_y=None,
                                        height='32dp')
        btn_salvar_meta.color = (0.12, 0.14, 0.18, 1)
        btn_salvar_meta.font_size = '12sp'
        btn_salvar_meta.bold = True
        btn_salvar_meta.bind(on_release=self.aplicar_filtro_meta)

        box_meta_card.add_widget(lbl_meta_tit)
        box_meta_card.add_widget(self.input_meta_selecionada)
        box_meta_card.add_widget(btn_salvar_meta)
        content.add_widget(box_meta_card)

        # Cabeçalho da Tabela
        self.table_header = GridLayout(cols=6, size_hint_y=None, height='32dp', spacing=3)
        self.lbl_col_hora = Label(text='HORA', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='11sp')
        self.lbl_col_hxh = Label(text='Meta HxH', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='11sp')
        self.lbl_col_cap = Label(text='Capacidade', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='11sp')
        self.lbl_col_res = Label(text='Resultado', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='11sp')
        self.lbl_col_status = Label(text='Produzido', color=(0.1, 0.45, 0.2, 1), bold=True, font_size='11sp')
        self.lbl_col_delta = Label(text='Delta', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='11sp')

        self.montar_cabecalho()
        content.add_widget(self.table_header)

        self.dados_tabela = [
            ('16:00 ás 17:00', 100, 100, 50),
            ('17:00 ás 18:00', 100, 200, 100),
            ('18:15 ás 19:00', 67, 267, 133.5),
            ('19:00 ás 19:15', 19, 286, 143),
            ('20:15 ás 21:00', 67, 353, 176.5),
            ('21:00 ás 22:00', 100, 453, 226.5),
            ('22:00 ás 23:00', 100, 553, 276.5),
            ('23:15 ás 00:00', 67, 620, 310),
            ('00:00 ás 01:09', 100, 720, 360),
        ]

        self.linhas_widgets = []
        for hora, hxh_val, m720, m360 in self.dados_tabela:
            row = GridLayout(cols=6, size_hint_y=None, height='38dp', spacing=3)
            lbl_h = Label(text=hora, color=(0.12, 0.14, 0.18, 1), font_size='10sp')
            lbl_hxh = Label(text=str(hxh_val), color=(0.12, 0.14, 0.18, 1), font_size='11sp')
            lbl_cap = Label(text=str(m720), color=(0.12, 0.14, 0.18, 1), font_size='11sp')
            txt_resultado = TextInput(text='', hint_text='Qtd', multiline=False, font_size='12sp', halign='center')
            lbl_status = Label(text='', bold=True, font_size='12sp')
            lbl_delta = Label(text='', bold=True, font_size='12sp')

            linha_data = {
                'row_widget': row, 'lbl_h': lbl_h, 'lbl_hxh': lbl_hxh,
                'lbl_cap': lbl_cap, 'txt_res': txt_resultado,
                'lbl_status': lbl_status, 'lbl_delta': lbl_delta,
                'val_720': m720, 'val_360': m360
            }

            txt_resultado.bind(text=lambda inst, val: self.recalcular_tabela())

            self.linhas_widgets.append(linha_data)
            self.montar_linha(linha_data)
            content.add_widget(row)

        box_totais = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10, padding=[0, 5])
        self.lbl_total_pos = Label(text='Total Positivo: +0', color=(0, 0.5, 0, 1), bold=True, font_size='13sp')
        self.lbl_total_neg = Label(text='Total Negativo: -0', color=(0.8, 0, 0, 1), bold=True, font_size='13sp')
        box_totais.add_widget(self.lbl_total_pos)
        box_totais.add_widget(self.lbl_total_neg)
        content.add_widget(box_totais)

        # Botões de ação mais claros, modernos e arredondados
        box_botoes = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp', spacing=8)

        btn_calcular = RoundedButton(text='CALCULAR', bg_color=(0.25, 0.65, 0.85, 1))
        btn_calcular.color = (1, 1, 1, 1)
        btn_calcular.bold = True
        btn_calcular.font_size = '12sp'
        btn_calcular.bind(on_release=self.calcular_totais)

        btn_salvar = RoundedButton(text='SALVAR', bg_color=(0.25, 0.7, 0.4, 1))
        btn_salvar.color = (1, 1, 1, 1)
        btn_salvar.bold = True
        btn_salvar.font_size = '12sp'
        btn_salvar.bind(on_release=self.salvar_dados)

        btn_compartilhar = RoundedButton(text='COMPARTILHAR', bg_color=(0.9, 0.6, 0.2, 1))
        btn_compartilhar.color = (1, 1, 1, 1)
        btn_compartilhar.bold = True
        btn_compartilhar.font_size = '11sp'
        btn_compartilhar.bind(on_release=self.compartilhar_dados)

        box_botoes.add_widget(btn_calcular)
        box_botoes.add_widget(btn_salvar)
        box_botoes.add_widget(btn_compartilhar)
        content.add_widget(box_botoes)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        main_layout.add_widget(CriarBarraNavegacao(ativa='producao'))
        self.add_widget(main_layout)

    def limpar_campos(self):
        for item in self.linhas_widgets:
            item['txt_res'].text = ''
            item['lbl_status'].text = ''
            item['lbl_delta'].text = ''
        self.lbl_total_pos.text = 'Total Positivo: +0'
        self.lbl_total_neg.text = 'Total Negativo: -0'
        perfil = obter_perfil_atual()
        self.input_meta_selecionada.text = str(perfil["meta_hoje"])

    def montar_cabecalho(self):
        self.table_header.clear_widgets()
        self.table_header.add_widget(self.lbl_col_hora)
        self.table_header.add_widget(self.lbl_col_hxh)
        self.table_header.add_widget(self.lbl_col_cap)
        self.table_header.add_widget(self.lbl_col_res)
        self.table_header.add_widget(self.lbl_col_status)
        self.table_header.add_widget(self.lbl_col_delta)

    def montar_linha(self, item):
        row = item['row_widget']
        row.clear_widgets()
        row.add_widget(item['lbl_h'])
        row.add_widget(item['lbl_hxh'])
        row.add_widget(item['lbl_cap'])
        row.add_widget(item['txt_res'])
        row.add_widget(item['lbl_status'])
        row.add_widget(item['lbl_delta'])

    def aplicar_filtro_meta(self, instance):
        valor_digitado = self.input_meta_selecionada.text.strip()
        meta_ativa = '360' if '360' in valor_digitado else '720'
        self.input_meta_selecionada.text = meta_ativa
        perfil = obter_perfil_atual()
        perfil["meta_hoje"] = int(meta_ativa)
        salvar_dados_gerais()

        for i, item in enumerate(self.linhas_widgets):
            val_base = self.dados_tabela[i][2] if meta_ativa == '720' else self.dados_tabela[i][3]
            item['lbl_cap'].text = str(val_base)

        self.recalcular_tabela()

    def recalcular_tabela(self):
        resultado_anterior = 0

        for i, item in enumerate(self.linhas_widgets):
            txt = item['txt_res'].text.strip()
            label_status = item['lbl_status']
            label_delta = item['lbl_delta']

            if txt.isdigit():
                val_resultado = int(txt)
                capacidade_acumulada = float(item['lbl_cap'].text)

                # Produção HxH da hora
                if i == 0:
                    producao_hora = val_resultado
                else:
                    producao_hora = val_resultado - resultado_anterior

                label_status.text = str(producao_hora)
                label_status.color = (0.05, 0.55, 0.25, 1)  # Verde bonito e elegante para a coluna Produzido

                # Delta (Desvio em relação à Capacidade)
                delta_val = int(val_resultado - capacidade_acumulada)

                if delta_val > 0:
                    label_delta.text = f'+{delta_val}'
                    label_delta.color = (0.0, 0.5, 0.0, 1)
                elif delta_val < 0:
                    label_delta.text = f'{delta_val}'
                    label_delta.color = (0.8, 0.0, 0.0, 1)
                else:
                    label_delta.text = '0'
                    label_delta.color = (0.12, 0.14, 0.18, 1)

                resultado_anterior = val_resultado
            else:
                label_status.text = ''
                label_delta.text = ''

    def calcular_totais(self, instance):
        total_pos = 0
        total_neg = 0
        ultimo_resultado = 0

        for item in self.linhas_widgets:
            txt = item['txt_res'].text.strip()
            if txt.isdigit():
                val_linha = int(txt)
                ultimo_resultado = val_linha
                capacidade_acumulada = float(item['lbl_cap'].text)
                dif = val_linha - capacidade_acumulada
                if dif >= 0:
                    total_pos += dif
                else:
                    total_neg += abs(dif)

        self.lbl_total_pos.text = f'Total Positivo: +{int(total_pos)}'
        self.lbl_total_neg.text = f'Total Negativo: -{int(total_neg)}'

        perfil = obter_perfil_atual()
        perfil["total_produzido_hoje"] = ultimo_resultado
        meta = perfil["meta_hoje"]
        perfil["porcentagem_hoje"] = (ultimo_resultado / meta) * 100 if meta > 0 else 0
        salvar_dados_gerais()

    def gerar_texto_relatorio(self):
        meta_tipo = self.input_meta_selecionada.text.strip()
        texto_msg = f"*Acompanhamento de Produção (Meta {meta_tipo})*\n*Operador:* {DADOS_APP['usuario_atual']}\n\n"
        resultado_anterior = 0

        for i, item in enumerate(self.linhas_widgets):
            hora = item['lbl_h'].text
            capacidade_h = item['lbl_cap'].text
            res_txt = item['txt_res'].text.strip()

            if res_txt.isdigit():
                val_res = int(res_txt)
                prod_hora = val_res if i == 0 else val_res - resultado_anterior
                delta = int(val_res - float(capacidade_h))

                emoji = "🟢" if delta >= 0 else "❌"
                texto_msg += f"{hora} | Cap:{capacidade_h} | Real:{val_res} (Produzido:{prod_hora} | Delta:{delta:+d}) {emoji}\n"
                resultado_anterior = val_res
            else:
                texto_msg += f"{hora} | Cap:{capacidade_h} | --\n"

        return texto_msg

    def salvar_dados(self, instance):
        self.calcular_totais(instance)
        relatorio = self.gerar_texto_relatorio()
        perfil = obter_perfil_atual()
        perfil["historico_salvo"].append(relatorio)

        qtd_salvos = len(perfil["historico_salvo"])
        perfil["oee_semana"] = min(100.0, 85.0 + (qtd_salvos * 2.5))
        perfil["meta_mes_pct"] = min(100.0, perfil["porcentagem_hoje"])
        salvar_dados_gerais()

        self.lbl_total_pos.text = "Salvo com sucesso! Atualizado no Início ✅"

    def compartilhar_dados(self, instance):
        texto_msg = self.gerar_texto_relatorio()
        Clipboard.copy(texto_msg)
        if has_plyer:
            try:
                share.share(text=texto_msg, title='Compartilhar Produção')
            except Exception as e:
                print("Erro ao compartilhar:", e)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# 4. TELA DE CONFIGURAÇÕES
# ==========================================
class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical')

        with main_layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.size)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))
        header.add_widget(
            Label(text='CONFIGURAÇÕES E BANCO DE DADOS', color=(1.0, 0.82, 0.0, 1), font_size='15sp', bold=True))
        main_layout.add_widget(header)

        conteudo = BoxLayout(orientation='vertical', padding=25, spacing=15)

        lbl_info = Label(
            text='Gerencie o Banco de Dados do Aplicativo.\nTodas as produções, fotos e usuários são salvos automaticamente na planilha compatível com Excel.',
            color=(0.12, 0.14, 0.18, 1),
            font_size='13sp',
            halign='center'
        )
        lbl_info.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        conteudo.add_widget(lbl_info)

        self.lbl_status_planilha = Label(
            text='Status: Planilha CSV atualizada com sucesso.',
            color=(0.1, 0.5, 0.1, 1),
            font_size='12sp',
            bold=True
        )
        conteudo.add_widget(self.lbl_status_planilha)

        btn_baixar_planilha = Button(
            text='📥 BAIXAR / ATUALIZAR PLANILHA (EXCEL/CSV)',
            size_hint_y=None,
            height='50dp',
            background_color=(1.0, 0.82, 0.0, 1),
            color=(0.12, 0.14, 0.18, 1),
            bold=True,
            font_size='13sp'
        )
        btn_baixar_planilha.bind(on_release=self.exportar_planilha)
        conteudo.add_widget(btn_baixar_planilha)
        conteudo.add_widget(Label())

        main_layout.add_widget(conteudo)
        main_layout.add_widget(CriarBarraNavegacao(ativa='config'))
        self.add_widget(main_layout)

    def exportar_planilha(self, instance):
        gerar_planilha_csv()
        self.lbl_status_planilha.text = 'Sucesso! Salvo como "mybag_banco_dados.csv" (Abra direto no Excel) ✅'

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# 5. TELA DE SUPORTE
# ==========================================
class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        super_layout = BoxLayout(orientation='vertical')

        with super_layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=super_layout.size, pos=super_layout.size)
        super_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))
        header.add_widget(Label(text='SUPORTE TÉCNICO', color=(1.0, 0.82, 0.0, 1), font_size='17sp', bold=True))
        super_layout.add_widget(header)

        conteudo = BoxLayout(orientation='vertical', padding=20, spacing=10)
        conteudo.add_widget(
            Label(text='Suporte José Nilton Multiplicador', color=(0.12, 0.14, 0.18, 1), font_size='16sp', bold=True))
        conteudo.add_widget(
            Label(text='WhatsApp para Contato:\n81 99697-4733', color=(0.4, 0.3, 0.2, 1), font_size='14sp',
                  halign='center'))
        conteudo.add_widget(Label())

        super_layout.add_widget(conteudo)
        super_layout.add_widget(CriarBarraNavegacao(ativa='suporte'))
        self.add_widget(super_layout)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# BARRA DE NAVEGAÇÃO GLOBAL
# ==========================================
class CriarBarraNavegacao(GridLayout):
    def __init__(self, ativa='', **kwargs):
        super().__init__(**kwargs)
        self.cols = 5
        self.size_hint_y = None
        self.height = '62dp'

        with self.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.nav_bg = Rectangle(size=self.size, pos=self.size)
        self.bind(size=lambda inst, val: setattr(self.nav_bg, 'size', inst.size),
                  pos=lambda inst, val: setattr(self.nav_bg, 'pos', inst.pos))

        botoes = [
            ('Início', 'inicio'),
            ('Relat.', 'relatorios'),
            ('Produção', 'producao'),
            ('Config.', 'config'),
            ('Suporte', 'suporte')
        ]

        for nome, tela in botoes:
            is_active = (tela == ativa)
            btn = Button(
                text=nome,
                font_size='14sp',
                background_color=(0, 0, 0, 0),
                color=(1.0, 0.82, 0.0, 1) if is_active else (0.85, 0.88, 0.92, 1),
                bold=True
            )
            btn.bind(on_release=lambda inst, t=tela: self.mudar_tela(t))
            self.add_widget(btn)

    def mudar_tela(self, nome_tela):
        app = App.get_running_app()
        if nome_tela == 'producao':
            prod_screen = app.sm.get_screen('producao')
            prod_screen.limpar_campos()
        app.sm.current = nome_tela


# ==========================================
# APP PRINCIPAL
# ==========================================
class ProductionApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(WelcomeScreen(name='welcome'))
        self.sm.add_widget(HomeScreen(name='inicio'))
        self.sm.add_widget(ReportsScreen(name='relatorios'))
        self.sm.add_widget(ProductionScreen(name='producao'))
        self.sm.add_widget(ConfigScreen(name='config'))
        self.sm.add_widget(SupportScreen(name='suporte'))

        self.sm.current = 'welcome'
        return self.sm


if __name__ == '__main__':
    ProductionApp().run()