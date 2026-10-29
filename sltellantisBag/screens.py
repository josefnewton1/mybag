from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock

# Verificação e importação para leitura de QR Code e Câmera no Android
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    has_android = True
except ImportError:
    has_android = False

from database import DADOS_APP, obter_perfil_atual, salvar_dados_gerais
from components import CircularAvatar, RoundedButton, CriarBarraNavegacao, abrir_seletor_foto


# ==========================================
# TELA DE BOAS-VINDAS / LOGIN
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
        container_avatar = BoxLayout(orientation='vertical', size_hint=(None, None), size=('85dp', '85dp'),
                                     pos_hint={'center_x': 0.5})
        self.avatar_real = CircularAvatar(size=('85dp', '85dp'))
        container_avatar.add_widget(self.avatar_real)
        main_layout.add_widget(container_avatar)

        btn_trocar = Button(text='Alterar GIF de Perfil', size_hint=(None, None), size=('160dp', '30dp'),
                            pos_hint={'center_x': 0.5}, background_color=(0.12, 0.14, 0.18, 1),
                            color=(1.0, 0.82, 0.0, 1), bold=True, font_size='11sp')
        btn_trocar.bind(on_release=lambda x: abrir_seletor_foto(self.carregar_foto_usuario))
        main_layout.add_widget(btn_trocar)

        box_input = BoxLayout(orientation='vertical', size_hint_y=None, height='75dp', spacing=5)
        lbl_instrucao = Label(text='Seu Nome Completo (Usuário):', color=(0.12, 0.14, 0.18, 1), font_size='12sp',
                              bold=True, halign='left')
        lbl_instrucao.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        self.input_nome = TextInput(text=DADOS_APP["usuario_atual"], multiline=False, font_size='14sp',
                                    size_hint_y=None, height='38dp', halign='center')
        self.input_nome.bind(text=self.ao_mudar_nome)
        box_input.add_widget(lbl_instrucao)
        box_input.add_widget(self.input_nome)
        main_layout.add_widget(box_input)

        btn_entrar = Button(text='ENTRAR NO SISTEMA', size_hint_y=None, height='48dp',
                            background_color=(1.0, 0.82, 0.0, 1), color=(0.12, 0.14, 0.18, 1), bold=True,
                            font_size='15sp')
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
        app.sm.get_screen('inicio').atualizar_dados_dashboard()
        app.sm.current = 'inicio'

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# TELA DE INÍCIO (PAINEL DE CONTROLE)
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
        header.add_widget(
            Label(text='PAINEL DE CONTROLE - MYBAG', color=(1.0, 0.82, 0.0, 1), font_size='16sp', bold=True,
                  halign='center'))
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

        lbl_acoes = Label(text='AÇÕES RÁPIDAS', color=(0.4, 0.3, 0.2, 1), font_size='12sp', bold=True, size_hint_y=None,
                          height='24dp', halign='left')
        lbl_acoes.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.content.add_widget(lbl_acoes)

        btn_ir_producao = Button(text='+ REGISTRAR PRODUÇÃO', size_hint_y=None, height='45dp',
                                 background_color=(1.0, 0.82, 0.0, 1), color=(0.12, 0.14, 0.18, 1), bold=True,
                                 font_size='14sp')
        btn_ir_producao.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'producao'))
        self.content.add_widget(btn_ir_producao)

        btn_ir_relatorios = Button(text='📊 VER DASHBOARD DE RELATÓRIOS', size_hint_y=None, height='45dp',
                                   background_color=(0.18, 0.22, 0.28, 1), color=(1.0, 0.82, 0.0, 1), bold=True,
                                   font_size='13sp')
        btn_ir_relatorios.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'relatorios'))
        self.content.add_widget(btn_ir_relatorios)

        btn_contagem_camera = Button(text='📷 ABRIR CÂMERA E CONTAR ITENS', size_hint_y=None, height='45dp',
                                     background_color=(0.2, 0.6, 0.8, 1), color=(1, 1, 1, 1), bold=True,
                                     font_size='13sp')
        btn_contagem_camera.bind(on_release=self.abrir_camera_contagem)
        self.content.add_widget(btn_contagem_camera)

        scroll.add_widget(self.content)
        self.main_layout.add_widget(scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='inicio'))
        self.add_widget(self.main_layout)

    def abrir_camera_contagem(self, instance):
        Popup(title='Câmera de Contagem', content=Label(text='Módulo de contagem visual via câmera ativado!'),
              size_hint=(0.8, 0.3)).open()

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

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# TELA DE DASHBOARD DE RELATÓRIOS
# ==========================================
class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        with self.main_layout.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.size)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.08, 0.10, 0.13, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))
        header.add_widget(
            Label(text='📊 DASHBOARD EXECUTIVO - RELATÓRIOS', color=(1.0, 0.82, 0.0, 1), font_size='16sp', bold=True))
        self.main_layout.add_widget(header)

        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=14, padding=14)
        self.content.bind(minimum_height=self.content.setter('height'))

        self.grid_kpi = GridLayout(cols=2, size_hint_y=None, height='110dp', spacing=10)
        self.card_meta = self.criar_card_kpi("META DIÁRIA", "0 un", (0.2, 0.6, 0.8, 1))
        self.card_prod = self.criar_card_kpi("PRODUZIDO HOJE", "0 un", (0.2, 0.7, 0.4, 1))
        self.grid_kpi.add_widget(self.card_meta['layout'])
        self.grid_kpi.add_widget(self.card_prod['layout'])
        self.content.add_widget(self.grid_kpi)

        self.card_status = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=12, spacing=6)
        with self.card_status.canvas.before:
            Color(0.18, 0.22, 0.28, 1)
            self.cs_bg = RoundedRectangle(size=self.card_status.size, pos=self.card_status.pos, radius=[12])
        self.card_status.bind(size=lambda inst, val: setattr(self.cs_bg, 'size', inst.size),
                              pos=lambda inst, val: setattr(self.cs_bg, 'pos', inst.pos))

        self.lbl_status_tit = Label(text='EFICIÊNCIA GERAL DA OPERAÇÃO', color=(0.8, 0.8, 0.8, 1), font_size='11sp',
                                    bold=True)
        self.lbl_status_val = Label(text='0.0% Concluído', color=(1.0, 0.82, 0.0, 1), font_size='22sp', bold=True)
        self.lbl_status_det = Label(text='Aguardando novos registros de produção...', color=(0.7, 0.7, 0.7, 1),
                                    font_size='11sp')

        self.card_status.add_widget(self.lbl_status_tit)
        self.card_status.add_widget(self.lbl_status_val)
        self.card_status.add_widget(self.lbl_status_det)
        self.content.add_widget(self.card_status)

        lbl_hist_tit = Label(text='REGISTROS RECENTES NO DASHBOARD', color=(1.0, 0.82, 0.0, 1), font_size='13sp',
                             bold=True, size_hint_y=None, height='30dp', halign='left')
        lbl_hist_tit.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.content.add_widget(lbl_hist_tit)

        self.historico_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.content.add_widget(self.historico_container)

        self.scroll.add_widget(self.content)
        self.main_layout.add_widget(self.scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='relatorios'))
        self.add_widget(self.main_layout)

    def criar_card_kpi(self, titulo, valor_inicial, cor_borda):
        card = BoxLayout(orientation='vertical', padding=10, spacing=4)
        with card.canvas.before:
            Color(0.18, 0.22, 0.28, 1)
            bg = RoundedRectangle(size=card.size, pos=card.pos, radius=[10])
        card.bind(size=lambda inst, val: setattr(bg, 'size', inst.size),
                  pos=lambda inst, val: setattr(bg, 'pos', inst.pos))
        lbl_t = Label(text=titulo, color=(0.7, 0.7, 0.7, 1), font_size='10sp', bold=True)
        lbl_v = Label(text=valor_inicial, color=cor_borda, font_size='18sp', bold=True)
        card.add_widget(lbl_t)
        card.add_widget(lbl_v)
        return {'layout': card, 'label_valor': lbl_v}

    def on_enter(self):
        perfil = obter_perfil_atual()
        meta = perfil["meta_hoje"]
        total = perfil["total_produzido_hoje"]
        pct = perfil["porcentagem_hoje"]

        self.card_meta['label_valor'].text = f"{meta} un"
        self.card_prod['label_valor'].text = f"{total} un"
        self.lbl_status_val.text = f"{pct:.1f}% Concluído"

        if pct >= 100:
            self.lbl_status_det.text = "Status: Meta atingida com sucesso! 🟢"
        elif pct >= 80:
            self.lbl_status_det.text = "Status: Próximo da meta, ritmo estável. ⚠️"
        else:
            self.lbl_status_det.text = "Status: Abaixo da meta esperada. ❌"

        self.historico_container.clear_widgets()
        historico = perfil.get("historico_salvo", [])
        if not historico:
            lbl_vazio = Label(text='Nenhum dado registrado no histórico ainda.', color=(0.5, 0.5, 0.5, 1),
                              font_size='12sp', size_hint_y=None, height='40dp')
            self.historico_container.add_widget(lbl_vazio)
            self.historico_container.height = 40
        else:
            self.historico_container.height = len(historico) * 75
            for h in historico:
                item_box = BoxLayout(orientation='vertical', size_hint_y=None, height='65dp', padding=8)
                with item_box.canvas.before:
                    Color(0.15, 0.18, 0.24, 1)
                    bg_i = RoundedRectangle(size=item_box.size, pos=item_box.pos, radius=[8])
                item_box.bind(size=lambda inst, val: setattr(bg_i, 'size', inst.size),
                              pos=lambda inst, val: setattr(bg_i, 'pos', inst.pos))
                lbl_texto = Label(text=h, color=(0.9, 0.9, 0.9, 1), font_size='10sp', halign='left', valign='middle')
                lbl_texto.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
                item_box.add_widget(lbl_texto)
                self.historico_container.add_widget(item_box)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# TELA DE PRODUÇÃO & H X H
# ==========================================
class ProductionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical')
        with main_layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=lambda inst, val: setattr(self.bg_rect, 'size', inst.size), pos=lambda inst, val: setattr(self.bg_rect, 'pos', inst.pos))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size), pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))
        header.add_widget(Label(text='ACOMPANHAMENTO DE PRODUÇÃO', color=(1.0, 0.82, 0.0, 1), font_size='17sp', bold=True))
        main_layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=12, padding=12)
        content.bind(minimum_height=content.setter('height'))

        box_meta_card = BoxLayout(orientation='vertical', size_hint_y=None, height='95dp', padding=8, spacing=6)
        lbl_meta_tit = Label(text='DEFINIÇÃO DE META (720 ou 360)', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True, halign='center')
        lbl_meta_tit.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.input_meta_selecionada = TextInput(text='720', multiline=False, font_size='15sp', size_hint_y=None, height='35dp', halign='center')

        btn_salvar_meta = RoundedButton(text='Salvar Meta', bg_color=(0.85, 0.65, 0.1, 1), size_hint_y=None, height='32dp')
        btn_salvar_meta.color = (0.12, 0.14, 0.18, 1)
        btn_salvar_meta.font_size = '12sp'
        btn_salvar_meta.bold = True
        btn_salvar_meta.bind(on_release=self.aplicar_filtro_meta)

        box_meta_card.add_widget(lbl_meta_tit)
        box_meta_card.add_widget(self.input_meta_selecionada)
        box_meta_card.add_widget(btn_salvar_meta)
        content.add_widget(box_meta_card)

        self.table_header = GridLayout(cols=6, size_hint_y=None, height='32dp', spacing=3, size_hint_x=1)
        self.table_header.add_widget(Label(text='HORA', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='10sp', halign='center'))
        self.table_header.add_widget(Label(text='Meta', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='10sp', halign='center'))
        self.table_header.add_widget(Label(text='Cap.', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='10sp', halign='center'))
        self.table_header.add_widget(Label(text='Res.', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='10sp', halign='center'))
        self.table_header.add_widget(Label(text='Prod.', color=(0.1, 0.45, 0.2, 1), bold=True, font_size='10sp', halign='center'))
        self.table_header.add_widget(Label(text='Delta', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='10sp', halign='center'))
        content.add_widget(self.table_header)

        self.dados_hxh_base = [
            ("16:00-17:00", 100, 100, 50, 50),
            ("17:00-18:00", 100, 200, 50, 100),
            ("18:15-19:00", 67, 267, 34, 134),
            ("19:00-19:15", 19, 286, 9, 143),
            ("20:15-21:00", 67, 353, 34, 177),
            ("21:00-22:00", 100, 453, 50, 227),
            ("22:00-23:00", 100, 553, 50, 277),
            ("23:15-00:00", 67, 620, 34, 310),
            ("00:00-01:09", 100, 720, 50, 360),
        ]

        self.linhas_widgets = []
        self.tabela_linhas_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=4)

        for hora, h720, cap720, h360, cap360 in self.dados_hxh_base:
            # Correção crucial: size_hint_x=1 garante que a linha ocupe toda a largura da tela
            row = GridLayout(cols=6, size_hint_y=None, height='38dp', spacing=3, size_hint_x=1)
            lbl_h = Label(text=hora, color=(0.12, 0.14, 0.18, 1), font_size='9sp', halign='center')
            lbl_hxh = Label(text=str(h720), color=(0.12, 0.14, 0.18, 1), font_size='10sp', bold=True, halign='center')
            lbl_cap = Label(text=str(cap720), color=(0.12, 0.14, 0.18, 1), font_size='10sp', halign='center')
            txt_res = TextInput(text='', hint_text='Qtd', multiline=False, font_size='11sp', halign='center')
            lbl_prod = Label(text='0', color=(0.1, 0.5, 0.1, 1), bold=True, font_size='11sp', halign='center')
            lbl_delta = Label(text='+0', color=(0.1, 0.5, 0.1, 1), bold=True, font_size='11sp', halign='center')

            linha_info = {
                'row': row, 'lbl_h': lbl_h, 'lbl_hxh': lbl_hxh, 'lbl_cap': lbl_cap,
                'txt_res': txt_res, 'lbl_prod': lbl_prod, 'lbl_delta': lbl_delta,
                'h720': h720, 'cap720': cap720, 'h360': h360, 'cap360': cap360
            }
            txt_res.bind(text=lambda inst, val: self.calcular_totais(None))

            row.add_widget(lbl_h)
            row.add_widget(lbl_hxh)
            row.add_widget(lbl_cap)
            row.add_widget(txt_res)
            row.add_widget(lbl_prod)
            row.add_widget(lbl_delta)

            self.linhas_widgets.append(linha_info)
            self.tabela_linhas_layout.add_widget(row)

        self.tabela_linhas_layout.height = len(self.dados_hxh_base) * 42
        content.add_widget(self.tabela_linhas_layout)

        box_totais = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=10, padding=[0, 5])
        self.lbl_total_pos = Label(text='Total Positivo: +0', color=(0, 0.5, 0, 1), bold=True, font_size='12sp', halign='center')
        self.lbl_total_neg = Label(text='Total Negativo: -0', color=(0.8, 0, 0, 1), bold=True, font_size='12sp', halign='center')
        box_totais.add_widget(self.lbl_total_pos)
        box_totais.add_widget(self.lbl_total_neg)
        content.add_widget(box_totais)

        box_botoes = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp', spacing=8)
        btn_calcular = RoundedButton(text='CALCULAR', bg_color=(0.25, 0.65, 0.85, 1))
        btn_calcular.color = (1, 1, 1, 1); btn_calcular.bold = True; btn_calcular.font_size = '11sp'
        btn_calcular.bind(on_release=self.calcular_totais)

        btn_salvar = RoundedButton(text='SALVAR', bg_color=(0.25, 0.7, 0.4, 1))
        btn_salvar.color = (1, 1, 1, 1); btn_salvar.bold = True; btn_salvar.font_size = '11sp'
        btn_salvar.bind(on_release=self.salvar_dados)

        btn_compartilhar = RoundedButton(text='COMPARTILHAR', bg_color=(0.9, 0.6, 0.2, 1))
        btn_compartilhar.color = (1, 1, 1, 1); btn_compartilhar.bold = True; btn_compartilhar.font_size = '10sp'
        btn_compartilhar.bind(on_release=self.compartilhar_dados)

        box_botoes.add_widget(btn_calcular)
        box_botoes.add_widget(btn_salvar)
        box_botoes.add_widget(btn_compartilhar)
        content.add_widget(box_botoes)

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        main_layout.add_widget(CriarBarraNavegacao(ativa='producao'))
        self.add_widget(main_layout)

    def carregar_dados_iniciais(self):
        perfil = obter_perfil_atual()
        self.input_meta_selecionada.text = str(perfil.get("meta_hoje", 720))
        self.aplicar_filtro_meta(None)

    def aplicar_filtro_meta(self, instance):
        meta_str = self.input_meta_selecionada.text.strip()
        meta_val = 360 if '360' in meta_str else 720
        self.input_meta_selecionada.text = str(meta_val)
        perfil = obter_perfil_atual()
        perfil["meta_hoje"] = meta_val
        salvar_dados_gerais()

        for item in self.linhas_widgets:
            if meta_val == 360:
                item['lbl_hxh'].text = str(item['h360'])
                item['lbl_cap'].text = str(item['cap360'])
            else:
                item['lbl_hxh'].text = str(item['h720'])
                item['lbl_cap'].text = str(item['cap720'])
        self.calcular_totais(None)

    def calcular_totais(self, instance):
        total_prod_geral = 0
        total_pos = 0
        total_neg = 0
        meta_atual = int(self.input_meta_selecionada.text.strip() or 720)

        for item in self.linhas_widgets:
            txt = item['txt_res'].text.strip()
            meta_hxh = int(item['lbl_hxh'].text)
            if txt.isdigit():
                qtd = int(txt)
                total_prod_geral += qtd
                item['lbl_prod'].text = str(qtd)
                delta = qtd - meta_hxh
                item['lbl_delta'].text = f"+{delta}" if delta >= 0 else str(delta)
                if delta >= 0:
                    item['lbl_delta'].color = (0, 0.5, 0, 1)
                    total_pos += delta
                else:
                    item['lbl_delta'].color = (0.8, 0, 0, 1)
                    total_neg += abs(delta)
            else:
                item['lbl_prod'].text = "0"
                item['lbl_delta'].text = "+0"
                item['lbl_delta'].color = (0.5, 0.5, 0.5, 1)

        self.lbl_total_pos.text = f"Total Positivo: +{total_pos}"
        self.lbl_total_neg.text = f"Total Negativo: -{total_neg}"
        perfil = obter_perfil_atual()
        perfil["total_produzido_hoje"] = total_prod_geral
        if meta_atual > 0:
            perfil["porcentagem_hoje"] = (total_prod_geral / meta_atual) * 100
        salvar_dados_gerais()

    def salvar_dados(self, instance):
        self.calcular_totais(None)
        perfil = obter_perfil_atual()
        resumo = f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}\nMeta: {perfil['meta_hoje']} | Produzido: {perfil['total_produzido_hoje']} ({perfil['porcentagem_hoje']:.1f}%)\n{self.lbl_total_pos.text} | {self.lbl_total_neg.text}"
        perfil["historico_salvo"].insert(0, resumo)
        if len(perfil["historico_salvo"]) > 20:
            perfil["historico_salvo"].pop()
        salvar_dados_gerais()
        Popup(title='Sucesso', content=Label(text='Dados salvos com sucesso!'), size_hint=(0.8, 0.3)).open()

    def compartilhar_dados(self, instance):
        self.calcular_totais(None)
        perfil = obter_perfil_atual()
        texto = f"*RELATÓRIOS MYBAG*\nMeta: {perfil['meta_hoje']} | Produzido: {perfil['total_produzido_hoje']} ({perfil['porcentagem_hoje']:.1f}%)\n{self.lbl_total_pos.text} | {self.lbl_total_neg.text}"
        Clipboard.copy(texto)
        Popup(title='Compartilhar', content=Label(text='Relatório copiado para a área de transferência!'), size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

# TELA DE SUPORTE (APENAS CONTATO)
# ==========================================
class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        with layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda inst, val: setattr(self.bg_rect, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.bg_rect, 'pos', inst.pos))

        header = BoxLayout(size_hint_y=None, height='55dp', padding=10)
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            Rectangle(size=header.size, pos=header.size)
        header.add_widget(Label(text='SUPORTE TÉCNICO', color=(1.0, 0.82, 0.0, 1), bold=True, font_size='16sp'))
        layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=14, padding=16)
        content.bind(minimum_height=content.setter('height'))

        card_info = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', padding=14, spacing=8)
        with card_info.canvas.before:
            Color(0.18, 0.22, 0.28, 1)
            bg_c = RoundedRectangle(size=card_info.size, pos=card_info.pos, radius=[10])
        card_info.bind(size=lambda inst, val: setattr(bg_c, 'size', inst.size),
                       pos=lambda inst, val: setattr(bg_c, 'pos', inst.pos))

        lbl_suporte_tit = Label(text='CENTRAL DE ATENDIMENTO', color=(1.0, 0.82, 0.0, 1), font_size='13sp', bold=True)
        lbl_responsavel = Label(text='Responsável: José Nilton', color=(1, 1, 1, 1), font_size='12sp', halign='left')
        lbl_responsavel.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        lbl_tel = Label(text='Telefone/WhatsApp: (81) 99697-4723', color=(1, 1, 1, 1), font_size='12sp', halign='left')
        lbl_tel.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        card_info.add_widget(lbl_suporte_tit)
        card_info.add_widget(lbl_responsavel)
        card_info.add_widget(lbl_tel)
        content.add_widget(card_info)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        layout.add_widget(CriarBarraNavegacao(ativa='suporte'))
        self.add_widget(layout)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# ==========================================
# TELA DE TAREFAS / QR CODE
# ==========================================
class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        with layout.canvas.before:
            Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda inst, val: setattr(self.bg_rect, 'size', inst.size), pos=lambda inst, val: setattr(self.bg_rect, 'pos', inst.pos))

        header = BoxLayout(size_hint_y=None, height='55dp', padding=10)
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            Rectangle(size=header.size, pos=header.size)
        header.add_widget(Label(text='TAREFAS - LEITURA QR CODE', color=(1.0, 0.82, 0.0, 1), bold=True, font_size='16sp'))
        layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=14, padding=16)
        content.bind(minimum_height=content.setter('height'))

        lbl_instrucao = Label(
            text='Tarefas: Leia o QR Code 1 e em seguida o QR Code 2 de forma sequencial com a câmera.',
            color=(0.12, 0.14, 0.18, 1), font_size='12sp', halign='center', size_hint_y=None, height='40dp'
        )
        lbl_instrucao.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_instrucao)

        btn_ler_qr = Button(
            text='📷 ABRIR CÂMERA E LER QR CODES',
            size_hint_y=None, height='48dp',
            background_color=(1.0, 0.82, 0.0, 1), color=(0.12, 0.14, 0.18, 1), bold=True, font_size='13sp'
        )
        btn_ler_qr.bind(on_release=self.iniciar_leitura_qr_sequencial)
        content.add_widget(btn_ler_qr)

        content.add_widget(Label(text='QR Code 1:', color=(0.12, 0.14, 0.18, 1), font_size='12sp', bold=True, size_hint_y=None, height='20dp', halign='left'))
        self.input_qr1 = TextInput(text='', hint_text='Aguardando leitura do QR Code 1...', multiline=False, font_size='13sp', size_hint_y=None, height='38dp', readonly=True)
        content.add_widget(self.input_qr1)

        content.add_widget(Label(text='QR Code 2:', color=(0.12, 0.14, 0.18, 1), font_size='12sp', bold=True, size_hint_y=None, height='20dp', halign='left'))
        self.input_qr2 = TextInput(text='', hint_text='Aguardando leitura do QR Code 2...', multiline=False, font_size='13sp', size_hint_y=None, height='38dp', readonly=True)
        content.add_widget(self.input_qr2)

        btn_checar = Button(
            text='CHECAR DADOS',
            size_hint_y=None, height='48dp',
            background_color=(0.18, 0.22, 0.28, 1), color=(1.0, 0.82, 0.0, 1), bold=True, font_size='14sp'
        )
        btn_checar.bind(on_release=self.checar_dados_qr)
        content.add_widget(btn_checar)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        layout.add_widget(CriarBarraNavegacao(ativa='config'))
        self.add_widget(layout)

    def iniciar_leitura_qr_sequencial(self, instance):
        Popup(title='Leitor QR', content=Label(text='Iniciando leitura sequencial via câmera...'), size_hint=(0.8, 0.3)).open()

    def checar_dados_qr(self, instance):
        Popup(title='Checagem', content=Label(text='Checando dados dos QR Codes capturados...'), size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos