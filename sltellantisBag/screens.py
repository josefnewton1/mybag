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
from kivy.utils import platform

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


# Assumindo que já tens os teus componentes personalizados como RoundedButton
class UserProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Cabeçalho da Tela de Perfil
        header = Label(
            text='EDITAR PERFIL DO USUÁRIO',
            color=(1.0, 0.82, 0.0, 1),
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height='40dp'
        )
        self.main_layout.add_widget(header)

        # Formulário com os campos solicitados
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, height='350dp')

        self.inputs = {}
        campos = [
            ("Nome Completo", "nome_completo"),
            ("E-mail", "email"),
            ("Telefone", "telefone"),
            ("Função / Cargo", "funcao")
        ]

        for rotulo, chave in campos:
            box = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None, height='60dp')
            box.add_widget(Label(text=rotulo, font_size='12sp', color=(0.12, 0.14, 0.18, 1), halign='left'))

            txt_input = TextInput(
                text='',
                multiline=False,
                font_size='13sp',
                size_hint_y=None,
                height='35dp'
            )
            self.inputs[chave] = txt_input
            box.add_widget(txt_input)
            form_layout.add_widget(box)

        self.main_layout.add_widget(form_layout)

        # Botões de Ação Inferiores (Salvar, Apagar Campos, Excluir Perfil)
        botoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='45dp', spacing=10)

        btn_salvar = RoundedButton(text='Salvar', bg_color=(0.25, 0.7, 0.4, 1))
        btn_salvar.bind(on_release=self.salvar_perfil)

        btn_apagar = RoundedButton(text='Apagar Campos', bg_color=(0.85, 0.5, 0.1, 1))
        btn_apagar.bind(on_release=self.apagar_campos)

        btn_excluir = RoundedButton(text='Excluir Perfil', bg_color=(0.8, 0.2, 0.2, 1))
        btn_excluir.bind(on_release=self.excluir_perfil)

        botoes_layout.add_widget(btn_salvar)
        botoes_layout.add_widget(btn_apagar)
        botoes_layout.add_widget(btn_excluir)

        self.main_layout.add_widget(botoes_layout)

        # Botão para voltar à tela anterior (Configurações)
        btn_voltar = RoundedButton(text='Voltar', bg_color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height='40dp')
        btn_voltar.bind(on_release=self.voltar_config)
        self.main_layout.add_widget(btn_voltar)

        self.add_widget(self.main_layout)
        self.carregar_dados_salvos()

    def on_enter(self):
        # Sempre que entrar na tela, puxa os dados salvos mais recentes
        self.carregar_dados_salvos()

    def carregar_dados_salvos(self):
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            for chave, txt_input in self.inputs.items():
                txt_input.text = str(perfil.get(chave, ''))

    def salvar_perfil(self, instance):
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            for chave, txt_input in self.inputs.items():
                perfil[chave] = txt_input.text.strip()
            salvar_dados_gerais()  # Salva na planilha/base de dados interna

        Popup(title='Sucesso', content=Label(text='Informações do perfil salvas com sucesso!'),
              size_hint=(0.8, 0.3)).open()

    def apagar_campos(self, instance):
        # Limpa apenas os textos digitados nos inputs da tela atual
        for txt_input in self.inputs.values():
            txt_input.text = ''
        Popup(title='Apagar', content=Label(text='Campos limpos com sucesso!'), size_hint=(0.8, 0.3)).open()

    def excluir_perfil(self, instance):
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            for chave in self.inputs.keys():
                perfil[chave] = ''  # Reseta as informações na base de dados
            salvar_dados_gerais()
        self.apagar_campos(instance)
        Popup(title='Excluir', content=Label(text='Perfil apagado com sucesso!'), size_hint=(0.8, 0.3)).open()

    def voltar_config(self, instance):
        self.manager.current = 'config'  # Nome da tua tela de configurações no ScreenManager

# Verificação e importação para leitura de QR Code e Câmera no Android
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission

    has_android = True
except ImportError:
    has_android = False

from database import DADOS_APP, obter_perfil_atual, salvar_dados_gerais, obter_paleta_atual
from components import CircularAvatar, RoundedButton, CriarBarraNavegacao, abrir_seletor_foto


# ==========================================
# 1. TELA DE BOAS-VINDAS / LOGIN
# ==========================================
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        with main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
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

        self.input_nome = TextInput(text=DADOS_APP.get("usuario_atual", "José Nilton"), multiline=False,
                                    font_size='14sp',
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

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def ao_mudar_nome(self, instance, valor):
        nome_limpo = valor.strip()
        if nome_limpo:
            DADOS_APP["usuario_atual"] = nome_limpo
            obter_perfil_atual()
            self.carregar_foto_usuario()

    def carregar_foto_usuario(self):
        perfil = obter_perfil_atual()
        caminho_foto = perfil.get("foto_path", "") if isinstance(perfil, dict) else ""
        self.avatar_real.atualizar_imagem(caminho_foto)

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
# 2. TELA DE INÍCIO (PAINEL PRINCIPAL PROFISSIONAL)
# ==========================================
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')

        with self.main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Cabeçalho Superior Profissional
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 5])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

        header.add_widget(
            Label(text='STELLANTISBAG - INÍCIO', color=(1.0, 0.82, 0.0, 1), font_size='15sp', bold=True, halign='left'))
        self.main_layout.add_widget(header)

        # Scroll vertical para garantir fluidez em qualquer celular
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=16)
        content.bind(minimum_height=content.setter('height'))

        # Card de Boas-Vindas e Resumo do Perfil
        card_resumo = BoxLayout(orientation='vertical', size_hint_y=None, height='130dp', padding=14, spacing=8)
        with card_resumo.canvas.before:
            Color(0.18, 0.22, 0.28, 1)
            self.bg_card = RoundedRectangle(size=card_resumo.size, pos=card_resumo.pos, radius=[12])
        card_resumo.bind(size=lambda inst, val: setattr(self.bg_card, 'size', inst.size),
                         pos=lambda inst, val: setattr(self.bg_card, 'pos', inst.pos))

        perfil = obter_perfil_atual()
        nome_usuario = perfil.get('nome', 'Josef Newton') if isinstance(perfil, dict) else 'Josef Newton'
        meta_hoje = perfil.get('meta_hoje', 720) if isinstance(perfil, dict) else 720
        prod_hoje = perfil.get('total_produzido_hoje', 0) if isinstance(perfil, dict) else 0

        lbl_user = Label(text=f'👤 Olá, {nome_usuario}', color=(1.0, 0.82, 0.0, 1), font_size='14sp', bold=True,
                         halign='left')
        lbl_user.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        lbl_status = Label(text=f'Meta Atual: {meta_hoje} | Produzido: {prod_hoje}', color=(1, 1, 1, 1),
                           font_size='12sp', halign='left')
        lbl_status.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        lbl_linha = Label(text='📍 Setor: Montagem de Chicotes Elétricos', color=(0.8, 0.8, 0.8, 1), font_size='11sp',
                          halign='left')
        lbl_linha.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        card_resumo.add_widget(lbl_user)
        card_resumo.add_widget(lbl_status)
        card_resumo.add_widget(lbl_linha)
        content.add_widget(card_resumo)

        # Seção de Ações Principais (Botões lado a lado: Registrar e Dashboard)
        lbl_sec_acoes = Label(text='Ações Rápidas', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True,
                              size_hint_y=None, height='25dp', halign='left')
        lbl_sec_acoes.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_sec_acoes)

        box_botoes_principais = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)

        btn_registrar = RoundedButton(text='📝 REGISTRAR', bg_color=(0.25, 0.65, 0.85, 1))
        btn_registrar.color = (1, 1, 1, 1);
        btn_registrar.bold = True;
        btn_registrar.font_size = '12sp'
        btn_registrar.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'producao'))

        btn_dashboard = RoundedButton(text='📊 DASHBOARD', bg_color=(0.25, 0.7, 0.4, 1))
        btn_dashboard.color = (1, 1, 1, 1);
        btn_dashboard.bold = True;
        btn_dashboard.font_size = '12sp'
        btn_dashboard.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'relatorios'))

        box_botoes_principais.add_widget(btn_registrar)
        box_botoes_principais.add_widget(btn_dashboard)
        content.add_widget(box_botoes_principais)

        # Botão de Checagem direcionando para a tela 'checagem'
        btn_checagem = RoundedButton(text='📷 CHECAGEM', bg_color=(0.9, 0.6, 0.2, 1), size_hint_y=None, height='48dp')
        btn_checagem.color = (1, 1, 1, 1);
        btn_checagem.bold = True;
        btn_checagem.font_size = '12sp'
        btn_checagem.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'checagem'))
        content.add_widget(btn_checagem)

        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='inicio'))
        self.add_widget(self.main_layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def atualizar_dados_dashboard(self):
        pass

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
# ==========================================
# 3. TELA DE DASHBOARD DE RELATÓRIOS SIMPLIFICADA
# ==========================================
class ReportsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        with self.main_layout.canvas.before:
            self.bg_color = Color(0.12, 0.14, 0.18, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.size)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 10])
        with header.canvas.before:
            Color(0.08, 0.10, 0.13, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size), pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))
        header.add_widget(Label(text='📊 DASHBOARD EXECUTIVO', color=(1.0, 0.82, 0.0, 1), font_size='15sp', bold=True, halign='center'))
        self.main_layout.add_widget(header)

        self.scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=15)
        self.content.bind(minimum_height=self.content.setter('height'))

        self.grid_kpi = GridLayout(cols=2, size_hint_y=None, height='85dp', spacing=10)
        self.card_meta = self.criar_card_kpi("META DIÁRIA", "0 un", (0.2, 0.6, 0.8, 1))
        self.card_prod = self.criar_card_kpi("PRODUZIDO HOJE", "0 un", (0.2, 0.7, 0.4, 1))
        self.grid_kpi.add_widget(self.card_meta['layout'])
        self.grid_kpi.add_widget(self.card_prod['layout'])
        self.content.add_widget(self.grid_kpi)

        self.card_status = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=12, spacing=6)
        with self.card_status.canvas.before:
            Color(0.18, 0.22, 0.28, 1)
            self.cs_bg = RoundedRectangle(size=self.card_status.size, pos=self.card_status.pos, radius=[10])
        self.card_status.bind(size=lambda inst, val: setattr(self.cs_bg, 'size', inst.size), pos=lambda inst, val: setattr(self.cs_bg, 'pos', inst.pos))

        self.lbl_status_tit = Label(text='EFICIÊNCIA GERAL DA OPERAÇÃO', color=(0.8, 0.8, 0.8, 1), font_size='11sp', bold=True, size_hint_y=None, height='18dp')
        self.lbl_status_val = Label(text='0.0% Concluído', color=(1.0, 0.82, 0.0, 1), font_size='20sp', bold=True, size_hint_y=None, height='32dp')
        self.lbl_status_det = Label(text='Aguardando novos registros...', color=(0.7, 0.7, 0.7, 1), font_size='11sp', size_hint_y=None, height='20dp')

        self.card_status.add_widget(self.lbl_status_tit)
        self.card_status.add_widget(self.lbl_status_val)
        self.card_status.add_widget(self.lbl_status_det)
        self.content.add_widget(self.card_status)

        # Botão principal de apagar tudo / zerar os registros da operação
        self.btn_apagar_rel = Button(
            text='🗑️ APAGAR TUDO / ZERAR REGISTROS (0)',
            size_hint_y=None, height='48dp',
            background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), bold=True, font_size='12sp'
        )
        self.btn_apagar_rel.bind(on_release=self.apagar_todos_dados)
        self.content.add_widget(self.btn_apagar_rel)

        self.scroll.add_widget(self.content)
        self.main_layout.add_widget(self.scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='relatorios'))
        self.add_widget(self.main_layout)

    def criar_card_kpi(self, titulo, valor_inicial, cor_borda):
        card = BoxLayout(orientation='vertical', padding=6, spacing=2)
        with card.canvas.before:
            Color(0.18, 0.22, 0.28, 1)
            bg = RoundedRectangle(size=card.size, pos=card.pos, radius=[8])
        card.bind(size=lambda inst, val: setattr(bg, 'size', inst.size), pos=lambda inst, val: setattr(bg, 'pos', inst.pos))
        lbl_t = Label(text=titulo, color=(0.7, 0.7, 0.7, 1), font_size='9sp', bold=True, size_hint_y=None, height='15dp')
        lbl_v = Label(text=valor_inicial, color=cor_borda, font_size='15sp', bold=True, size_hint_y=None, height='25dp')
        card.add_widget(lbl_t)
        card.add_widget(lbl_v)
        return {'layout': card, 'label_valor': lbl_v}

    def apagar_todos_dados(self, instance):
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            perfil["total_produzido_hoje"] = 0
            perfil["porcentagem_hoje"] = 0.0
            perfil["historico_salvo"] = []
            salvar_dados_gerais()
        self.on_enter()
        Popup(title='Relatórios Zerados', content=Label(text='Todos os registros e dados foram apagados com sucesso!'), size_hint=(0.8, 0.3)).open()

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

        perfil = obter_perfil_atual()
        meta = perfil.get("meta_hoje", 720) if isinstance(perfil, dict) else 720
        total = perfil.get("total_produzido_hoje", 0) if isinstance(perfil, dict) else 0
        pct = perfil.get("porcentagem_hoje", 0.0) if isinstance(perfil, dict) else 0.0

        self.card_meta['label_valor'].text = f"{meta} un"
        self.card_prod['label_valor'].text = f"{total} un"
        self.lbl_status_val.text = f"{pct:.1f}% Concluído"

        if pct >= 100:
            self.lbl_status_det.text = "Status: Meta atingida! 🟢"
        elif pct >= 80:
            self.lbl_status_det.text = "Status: Próximo da meta. ⚠️"
        else:
            self.lbl_status_det.text = "Status: Abaixo da meta. ❌"

        historico = perfil.get("historico_salvo", []) if isinstance(perfil, dict) else []
        qtd_registros = len(historico)
        self.btn_apagar_rel.text = f'🗑️ APAGAR TUDO / ZERAR REGISTROS ({qtd_registros})'

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
#
# ==========================================
# 4. TELA DE PRODUÇÃO (REESTRUTURADA E PROFISSIONAL)
# ==========================================
class ProductionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')

        with self.main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Cabeçalho Superior Fixo
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='48dp', padding=[10, 5])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

        header.add_widget(
            Label(text='PAINEL DE CONTROLE - PRODUÇÃO', color=(1.0, 0.82, 0.0, 1), font_size='13sp', bold=True,
                  halign='center'))
        self.main_layout.add_widget(header)

        # Scroll vertical principal contendo todo o conteúdo organizado sequencialmente
        scroll_vertical = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        content.bind(minimum_height=content.setter('height'))

        # 1. BLOCO DE CONFIGURAÇÃO DE TURNO E META (Posicionado corretamente no topo)
        box_meta_card = BoxLayout(orientation='vertical', size_hint_y=None, height='110dp', padding=8, spacing=6)
        with box_meta_card.canvas.before:
            Color(0.90, 0.87, 0.80, 1)
            self.bg_card_meta = RoundedRectangle(size=box_meta_card.size, pos=box_meta_card.pos, radius=[8])
        box_meta_card.bind(size=lambda inst, val: setattr(self.bg_card_meta, 'size', inst.size),
                           pos=lambda inst, val: setattr(self.bg_card_meta, 'pos', inst.pos))

        lbl_meta_tit = Label(text='CONFIGURAÇÃO DO TURNO E META', color=(0.12, 0.14, 0.18, 1), font_size='10.5sp',
                             bold=True, halign='center')
        lbl_meta_tit.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        box_meta_card.add_widget(lbl_meta_tit)

        box_turno = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp', spacing=6)
        self.btn_turno_1 = Button(text='1º Turno (06:00)', background_color=(0.3, 0.3, 0.3, 1), color=(1, 1, 1, 1),
                                  bold=True, font_size='10sp')
        self.btn_turno_2 = Button(text='2º Turno (16:00)', background_color=(0.85, 0.65, 0.1, 1),
                                  color=(0.12, 0.14, 0.18, 1), bold=True, font_size='10sp')

        self.btn_turno_1.bind(on_release=lambda x: self.mudar_turno(1))
        self.btn_turno_2.bind(on_release=lambda x: self.mudar_turno(2))
        box_turno.add_widget(self.btn_turno_1)
        box_turno.add_widget(self.btn_turno_2)
        box_meta_card.add_widget(box_turno)

        box_meta_input = BoxLayout(orientation='horizontal', size_hint_y=None, height='30dp', spacing=6)
        perfil_inicial = obter_perfil_atual()
        meta_inicial = str(perfil_inicial.get("meta_hoje", 720) if isinstance(perfil_inicial, dict) else 720)
        self.input_meta_selecionada = TextInput(text=meta_inicial, multiline=False, font_size='12sp', size_hint_y=None,
                                                height='30dp', halign='center')

        btn_salvar_meta = RoundedButton(text='Aplicar Meta', bg_color=(0.25, 0.65, 0.85, 1), size_hint_y=None,
                                        height='30dp')
        btn_salvar_meta.color = (1, 1, 1, 1)
        btn_salvar_meta.font_size = '10sp'
        btn_salvar_meta.bold = True
        btn_salvar_meta.bind(on_release=self.aplicar_filtro_meta)

        box_meta_input.add_widget(self.input_meta_selecionada)
        box_meta_input.add_widget(btn_salvar_meta)
        box_meta_card.add_widget(box_meta_input)

        content.add_widget(box_meta_card)

        # 2. CABEÇALHO DA TABELA HORA A HORA
        lbl_tab_tit = Label(text='ACOMPANHAMENTO HORA A HORA', color=(0.12, 0.14, 0.18, 1), font_size='11sp', bold=True,
                            size_hint_y=None, height='22dp', halign='left')
        lbl_tab_tit.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_tab_tit)

        self.table_header = BoxLayout(orientation='horizontal', size_hint_y=None, height='26dp', spacing=1,
                                      size_hint_x=1)
        with self.table_header.canvas.before:
            Color(0.82, 0.78, 0.70, 1)
            self.bg_th = Rectangle(size=self.table_header.size, pos=self.table_header.pos)
        self.table_header.bind(size=lambda inst, val: setattr(self.bg_th, 'size', inst.size),
                               pos=lambda inst, val: setattr(self.bg_th, 'pos', inst.pos))

        self.table_header.add_widget(
            Label(text='HORA', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='8.5sp', halign='center',
                  size_hint_x=0.24))
        self.table_header.add_widget(
            Label(text='Meta', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='8.5sp', halign='center',
                  size_hint_x=0.12))
        self.table_header.add_widget(
            Label(text='Cap.', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='8.5sp', halign='center',
                  size_hint_x=0.12))
        self.table_header.add_widget(
            Label(text='Res.', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='8.5sp', halign='center',
                  size_hint_x=0.18))
        self.table_header.add_widget(
            Label(text='Prod.', color=(0.1, 0.45, 0.2, 1), bold=True, font_size='8.5sp', halign='center',
                  size_hint_x=0.17))
        self.table_header.add_widget(
            Label(text='Delta', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='8.5sp', halign='center',
                  size_hint_x=0.17))
        content.add_widget(self.table_header)

        self.turno_atual = 2

        self.dados_turno_2 = [
            ("16:00-17:00", 100, 100),
            ("17:00-18:00", 100, 200),
            ("18:15-19:00", 67, 267),
            ("19:00-19:15", 19, 286),
            ("20:15-21:00", 67, 353),
            ("21:00-22:00", 100, 453),
            ("22:00-23:00", 100, 553),
            ("23:15-00:00", 67, 620),
            ("00:00-01:09", 100, 720),
        ]

        self.dados_turno_1 = [
            ("06:00-07:00", 100, 100),
            ("07:00-08:00", 100, 200),
            ("08:15-09:00", 67, 267),
            ("09:00-09:15", 19, 286),
            ("10:15-11:00", 67, 353),
            ("11:00-12:00", 100, 453),
            ("12:45-13:45", 100, 553),
            ("13:45-14:30", 67, 620),
            ("14:30-15:43", 100, 720),
        ]

        self.linhas_widgets = []
        self.tabela_linhas_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2, size_hint_x=1)

        self.construir_linhas_tabela()
        content.add_widget(self.tabela_linhas_layout)

        # 3. PAINEL DE TOTAIS
        box_totais = BoxLayout(orientation='horizontal', size_hint_y=None, height='32dp', spacing=10, padding=[0, 2])
        self.lbl_total_pos = Label(text='Positivo: +0', color=(0, 0.5, 0, 1), bold=True, font_size='10sp',
                                   halign='center')
        self.lbl_total_neg = Label(text='Perdas Totais: 0', color=(0.8, 0, 0, 1), bold=True, font_size='10sp',
                                   halign='center')
        box_totais.add_widget(self.lbl_total_pos)
        box_totais.add_widget(self.lbl_total_neg)
        content.add_widget(box_totais)

        # 4. BOTÕES DE AÇÃO INFERIORES
        box_botoes = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing=6)
        btn_calcular = RoundedButton(text='CALCULAR', bg_color=(0.25, 0.65, 0.85, 1))
        btn_calcular.color = (1, 1, 1, 1);
        btn_calcular.bold = True;
        btn_calcular.font_size = '10sp'
        btn_calcular.bind(on_release=self.calcular_totais)

        btn_salvar = RoundedButton(text='SALVAR', bg_color=(0.25, 0.7, 0.4, 1))
        btn_salvar.color = (1, 1, 1, 1);
        btn_salvar.bold = True;
        btn_salvar.font_size = '10sp'
        btn_salvar.bind(on_release=self.salvar_dados)

        btn_compartilhar = RoundedButton(text='WHATSAPP', bg_color=(0.9, 0.6, 0.2, 1))
        btn_compartilhar.color = (1, 1, 1, 1);
        btn_compartilhar.bold = True;
        btn_compartilhar.font_size = '10sp'
        btn_compartilhar.bind(on_release=self.compartilhar_dados)

        box_botoes.add_widget(btn_calcular)
        box_botoes.add_widget(btn_salvar)
        box_botoes.add_widget(btn_compartilhar)
        content.add_widget(box_botoes)

        scroll_vertical.add_widget(content)
        self.main_layout.add_widget(scroll_vertical)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='producao'))
        self.add_widget(self.main_layout)

    def mudar_turno(self, turno):
        self.turno_atual = turno
        if turno == 1:
            self.btn_turno_1.background_color = (0.85, 0.65, 0.1, 1)
            self.btn_turno_1.color = (0.12, 0.14, 0.18, 1)
            self.btn_turno_2.background_color = (0.3, 0.3, 0.3, 1)
            self.btn_turno_2.color = (1, 1, 1, 1)
        else:
            self.btn_turno_2.background_color = (0.85, 0.65, 0.1, 1)
            self.btn_turno_2.color = (0.12, 0.14, 0.18, 1)
            self.btn_turno_1.background_color = (0.3, 0.3, 0.3, 1)
            self.btn_turno_1.color = (1, 1, 1, 1)

        self.construir_linhas_tabela()
        self.aplicar_filtro_meta(None)

    def construir_linhas_tabela(self):
        self.tabela_linhas_layout.clear_widgets()
        self.linhas_widgets = []

        dados_ativos = self.dados_turno_1 if self.turno_atual == 1 else self.dados_turno_2

        for hora, h720_meta, h720_cap in dados_ativos:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height='32dp', spacing=1, size_hint_x=1)

            lbl_h = Label(text=hora, color=(0.12, 0.14, 0.18, 1), font_size='8.5sp', halign='center', size_hint_x=0.24)
            lbl_hxh = Label(text=str(h720_meta), color=(0.12, 0.14, 0.18, 1), font_size='9sp', bold=True,
                            halign='center', size_hint_x=0.12)
            lbl_cap = Label(text=str(h720_cap), color=(0.12, 0.14, 0.18, 1), font_size='9sp', halign='center',
                            size_hint_x=0.12)
            txt_res = TextInput(text='', hint_text='Res.', multiline=False, font_size='10sp', halign='center',
                                size_hint_x=0.18)
            lbl_prod = Label(text='0', color=(0.1, 0.5, 0.1, 1), bold=True, font_size='9sp', halign='center',
                             size_hint_x=0.17)
            lbl_delta = Label(text='0', color=(0.1, 0.5, 0.1, 1), bold=True, font_size='9sp', halign='center',
                              size_hint_x=0.17)

            linha_info = {
                'row': row, 'lbl_h': lbl_h, 'lbl_hxh': lbl_hxh, 'lbl_cap': lbl_cap,
                'txt_res': txt_res, 'lbl_prod': lbl_prod, 'lbl_delta': lbl_delta,
                'base_meta': h720_meta, 'base_cap': h720_cap
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

        self.tabela_linhas_layout.height = len(dados_ativos) * 34

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def aplicar_filtro_meta(self, instance):
        meta_str = self.input_meta_selecionada.text.strip()
        meta_val = 360 if '360' in meta_str else 720
        self.input_meta_selecionada.text = str(meta_val)

        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            perfil["meta_hoje"] = meta_val
        salvar_dados_gerais()

        fator = 0.5 if meta_val == 360 else 1.0

        for item in self.linhas_widgets:
            nova_meta = int(item['base_meta'] * fator)
            nova_cap = int(item['base_cap'] * fator)
            item['lbl_hxh'].text = str(nova_meta)
            item['lbl_cap'].text = str(nova_cap)

        self.calcular_totais(None)

    def calcular_totais(self, instance):
        total_prod_geral = 0
        total_pos = 0
        total_neg = 0
        meta_atual = int(self.input_meta_selecionada.text.strip() or 720)

        acumulado_anterior = 0

        for i, item in enumerate(self.linhas_widgets):
            txt = item['txt_res'].text.strip()
            meta_hora = int(item['lbl_hxh'].text)

            if txt.isdigit():
                res_atual = int(txt)

                if i == 0:
                    prod_intervalo = res_atual
                else:
                    prod_intervalo = res_atual - acumulado_anterior

                item['lbl_prod'].text = str(prod_intervalo)
                total_prod_geral = res_atual

                delta = prod_intervalo - meta_hora
                item['lbl_delta'].text = str(delta) if delta < 0 else f"+{delta}"

                if delta >= 0:
                    item['lbl_delta'].color = (0, 0.5, 0, 1)
                    total_pos += delta
                else:
                    item['lbl_delta'].color = (0.8, 0, 0, 1)
                    total_neg += abs(delta)

                acumulado_anterior = res_atual
            else:
                item['lbl_prod'].text = "0"
                item['lbl_delta'].text = "0"
                item['lbl_delta'].color = (0.5, 0.5, 0.5, 1)

        self.lbl_total_pos.text = f"Positivo: +{total_pos}"
        self.lbl_total_neg.text = f"Perdas Totais: -{total_neg}"

        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            perfil["total_produzido_hoje"] = total_prod_geral
            if meta_atual > 0:
                perfil["porcentagem_hoje"] = (total_prod_geral / meta_atual) * 100
        salvar_dados_gerais()

    def salvar_dados(self, instance):
        self.calcular_totais(None)
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            meta = perfil.get('meta_hoje', 720)
            prod = perfil.get('total_produzido_hoje', 0)
            pct = perfil.get('porcentagem_hoje', 0.0)
            turno_nome = "1º Turno" if self.turno_atual == 1 else "2º Turno"
            resumo = f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')} ({turno_nome}) | Meta: {meta} | Prod: {prod} ({pct:.1f}%)"
            if "historico_salvo" not in perfil or not isinstance(perfil["historico_salvo"], list):
                perfil["historico_salvo"] = []
            perfil["historico_salvo"].insert(0, resumo)
            if len(perfil["historico_salvo"]) > 20:
                perfil["historico_salvo"].pop()
            salvar_dados_gerais()
        Popup(title='Sucesso', content=Label(text='Dados salvos com sucesso!'), size_hint=(0.8, 0.3)).open()

    def compartilhar_dados(self, instance):
        self.calcular_totais(None)
        perfil = obter_perfil_atual()
        meta_total = int(perfil.get('meta_hoje', 720) if isinstance(perfil, dict) else 720)
        prod_total = int(perfil.get('total_produzido_hoje', 0) if isinstance(perfil, dict) else 0)
        turno_nome = "1º Turno" if self.turno_atual == 1 else "2º Turno"

        detalhes_linhas = ""
        total_perdas = 0

        for item in self.linhas_widgets:
            hora = item['lbl_h'].text
            meta_hora = int(item['lbl_hxh'].text)
            txt_res = item['txt_res'].text.strip()

            if txt_res.isdigit():
                prod_intervalo = int(item['lbl_prod'].text)
                status_emoji = "✅" if prod_intervalo >= meta_hora else "❌"
                detalhes_linhas += f"*{hora}*={meta_hora}/{prod_intervalo}{status_emoji}\n"
                delta = prod_intervalo - meta_hora
                if delta < 0:
                    total_perdas += abs(delta)
            else:
                detalhes_linhas += f"*{hora}*={meta_hora}/\n"

        ope_calculado = (prod_total / meta_total * 100) if meta_total > 0 else 0.0

        texto = (
            f"*RELATÓRIOS MYBAG ({turno_nome})*\n\n"
            f"*226 portas anterior {turno_nome.lower()}*\n\n"
            f"*Previsto/Realizado*\n"
            f"{detalhes_linhas}\n"
            f"Refeição 🍽️\n\n"
            f"-------Fechamento----\n\n"
            f"*Produção prevista*: {meta_total}\n"
            f"*Produção realizada*: {prod_total}\n"
            f"Produção reportada: {prod_total}\n"
            f"*OPE*: {ope_calculado:.1f}%\n\n"
            f"SEMANAL:%\n"
            f"Perdas: -{total_perdas}\n"
            f"Motivo : "
        )

        Clipboard.copy(texto)

        try:
            import urllib.parse
            import webbrowser
            numero_whatsapp = "5581996974723"
            texto_codificado = urllib.parse.quote(texto)
            webbrowser.open(f"https://wa.me/{numero_whatsapp}?text={texto_codificado}")
        except Exception:
            pass

        Popup(title='Compartilhar', content=Label(text='Relatório formatado e pronto para o WhatsApp!'),
              size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
# ==========================================
# 6. TELA DE CONFIGURAÇÕES
# ==========================================
class ConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        with layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda inst, val: setattr(self.bg_rect, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.bg_rect, 'pos', inst.pos))

        header = BoxLayout(size_hint_y=None, height='55dp', padding=10)
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            Rectangle(size=header.size, pos=header.size)
        header.add_widget(Label(text='CONFIGURAÇÕES DO SISTEMA', color=(1.0, 0.82, 0.0, 1), bold=True, font_size='16sp',
                                halign='center'))
        layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=20)
        content.bind(minimum_height=content.setter('height'))

        lbl_titulo = Label(text='Preferências do Aplicativo', color=(0.12, 0.14, 0.18, 1), font_size='14sp', bold=True,
                           size_hint_y=None, height='30dp')
        content.add_widget(lbl_titulo)

        btn_perfil = RoundedButton(text='👤 Alterar Perfil / Usuário', bg_color=(0.18, 0.22, 0.28, 1), size_hint_y=None,
                                   height='48dp')
        btn_perfil.color = (1, 1, 1, 1)
        btn_perfil.bold = True
        btn_perfil.font_size = '13sp'
        # AQUI ESTÁ O SEGREDO: Faz o botão de perfil abrir a nova tela 'user_profile'
        btn_perfil.bind(on_release=lambda x: setattr(self.manager, 'current', 'user_profile'))

        btn_cores = RoundedButton(text='🎨 Alterar Cores e Tema', bg_color=(0.25, 0.65, 0.85, 1), size_hint_y=None,
                                  height='48dp')
        btn_cores.color = (1, 1, 1, 1)
        btn_cores.bold = True
        btn_cores.font_size = '13sp'
        btn_cores.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'theme_screen'))

        btn_notif = RoundedButton(text='🔔 Notificações e Alertas', bg_color=(0.25, 0.7, 0.4, 1), size_hint_y=None,
                                  height='48dp')
        btn_notif.color = (1, 1, 1, 1)
        btn_notif.bold = True
        btn_notif.font_size = '13sp'
        btn_notif.bind(on_release=self.acao_notificacoes)

        content.add_widget(btn_perfil)
        content.add_widget(btn_cores)
        content.add_widget(btn_notif)


        scroll.add_widget(content)
        layout.add_widget(scroll)
        layout.add_widget(CriarBarraNavegacao(ativa='config'))
        self.add_widget(layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def acao_notificacoes(self, instance):
        Popup(title='Notificações', content=Label(text='Configurações de alertas ativadas.'),
              size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
# ==========================================
# 7. TELA DE ESCOLHA DE TEMAS (3 OPÇÕES)
# ==========================================
class ThemeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        with layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda inst, val: setattr(self.bg_rect, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.bg_rect, 'pos', inst.pos))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[10, 5])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            Rectangle(size=header.size, pos=header.size)

        btn_voltar = Button(text='⬅ Voltar', size_hint_x=None, width='80dp', background_color=(0.2, 0.2, 0.2, 1),
                            color=(1, 1, 1, 1), bold=True, font_size='11sp')
        btn_voltar.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'config'))

        header.add_widget(btn_voltar)
        header.add_widget(
            Label(text='ESCOLHER TEMA DO APLICATIVO', color=(1.0, 0.82, 0.0, 1), bold=True, font_size='14sp',
                  halign='center'))
        layout.add_widget(header)

        content = BoxLayout(orientation='vertical', spacing=20, padding=30, size_hint_y=None, height='380dp',
                            pos_hint={'center_y': 0.5})

        lbl_instrucao = Label(text='Selecione o tema visual para todo o aplicativo:', color=(0.12, 0.14, 0.18, 1),
                              font_size='13sp', bold=True, halign='center')
        lbl_instrucao.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_instrucao)

        btn_tema1 = RoundedButton(text='☀️ Tema 1: Bege Clássico (Padrão)', bg_color=(0.96, 0.93, 0.88, 1),
                                  size_hint_y=None, height='50dp')
        btn_tema1.color = (0.12, 0.14, 0.18, 1);
        btn_tema1.bold = True;
        btn_tema1.font_size = '13sp'
        btn_tema1.bind(on_release=lambda x: self.aplicar_tema('padrao'))

        btn_tema2 = RoundedButton(text='🌙 Tema 2: Stellantis Dark (Escuro)', bg_color=(0.12, 0.14, 0.18, 1),
                                  size_hint_y=None, height='50dp')
        btn_tema2.color = (1.0, 0.82, 0.0, 1);
        btn_tema2.bold = True;
        btn_tema2.font_size = '13sp'
        btn_tema2.bind(on_release=lambda x: self.aplicar_tema('escuro'))

        btn_tema3 = RoundedButton(text='🔵 Tema 3: Azul Industrial', bg_color=(0.18, 0.35, 0.55, 1), size_hint_y=None,
                                  height='50dp')
        btn_tema3.color = (1, 1, 1, 1);
        btn_tema3.bold = True;
        btn_tema3.font_size = '13sp'
        btn_tema3.bind(on_release=lambda x: self.aplicar_tema('azul'))

        content.add_widget(btn_tema1)
        content.add_widget(btn_tema2)
        content.add_widget(btn_tema3)

        layout.add_widget(content)
        layout.add_widget(Label())
        self.add_widget(layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def aplicar_tema(self, nome_tema):
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            perfil["tema_atual"] = nome_tema
        salvar_dados_gerais()

        nomes_amigaveis = {'padrao': 'Bege Clássico', 'escuro': 'Stellantis Dark', 'azul': 'Azul Industrial'}
        msg = f"Tema '{nomes_amigaveis.get(nome_tema, nome_tema)}' aplicado!\nMude de tela para atualizar as cores."
        Popup(title='Tema Atualizado', content=Label(text=msg, halign='center'), size_hint=(0.85, 0.35)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos



# 7. TELA DE SUPORTE
# ==========================================
class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        with layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
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

        card_info = BoxLayout(orientation='vertical', size_hint_y=None, height='135dp', padding=14, spacing=8)
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

        # Botão para apagar todos os registros de relatório armazenados
        btn_zerar_suporte = Button(
            text='🗑️ APAGAR TODOS OS REGISTROS DE RELATÓRIO',
            size_hint_y=None, height='48dp',
            background_color=(0.8, 0.2, 0.2, 1), color=(1, 1, 1, 1), bold=True, font_size='12sp'
        )
        btn_zerar_suporte.bind(on_release=self.apagar_todos_registros_relatorio)
        content.add_widget(btn_zerar_suporte)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        layout.add_widget(CriarBarraNavegacao(ativa='suporte'))
        self.add_widget(layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def apagar_todos_registros_relatorio(self, instance):
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            perfil["total_produzido_hoje"] = 0
            perfil["porcentagem_hoje"] = 0.0
            perfil["historico_salvo"] = []  # Limpa o histórico da tela de relatórios
            salvar_dados_gerais()

        Popup(
            title='Registros Apagados',
            content=Label(text='Todos os registros e histórico da tela de relatório foram apagados com sucesso!'),
            size_hint=(0.8, 0.3)
        ).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
# ==========================================
# 9. TELA DE TAREFAS / LEITURA QR CODE E CÂMERA
# ==========================================
class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        with layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=lambda inst, val: setattr(self.bg_rect, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.bg_rect, 'pos', inst.pos))

        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[10, 5])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            Rectangle(size=header.size, pos=header.size)

        btn_voltar = Button(text='⬅ Voltar', size_hint_x=None, width='80dp', background_color=(0.2, 0.2, 0.2, 1),
                            color=(1, 1, 1, 1), bold=True, font_size='11sp')
        btn_voltar.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'producao'))

        header.add_widget(btn_voltar)
        header.add_widget(
            Label(text='TAREFAS - LEITURA QR CODE', color=(1.0, 0.82, 0.0, 1), bold=True, font_size='14sp',
                  halign='center'))
        layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=14, padding=16)
        content.bind(minimum_height=content.setter('height'))

        lbl_instrucao = Label(
            text='Tarefas: Leia o QR Code 1 e em seguida o QR Code 2 de forma sequencial com a câmera.',
            color=(0.12, 0.14, 0.18, 1), font_size='12sp', halign='center', size_hint_y=None, height='45dp'
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

        content.add_widget(
            Label(text='QR Code 1:', color=(0.12, 0.14, 0.18, 1), font_size='12sp', bold=True, size_hint_y=None,
                  height='20dp', halign='left'))
        self.input_qr1 = TextInput(text='', hint_text='Aguardando leitura do QR Code 1...', multiline=False,
                                   font_size='13sp', size_hint_y=None, height='38dp', readonly=True)
        content.add_widget(self.input_qr1)

        content.add_widget(
            Label(text='QR Code 2:', color=(0.12, 0.14, 0.18, 1), font_size='12sp', bold=True, size_hint_y=None,
                  height='20dp', halign='left'))
        self.input_qr2 = TextInput(text='', hint_text='Aguardando leitura do QR Code 2...', multiline=False,
                                   font_size='13sp', size_hint_y=None, height='38dp', readonly=True)
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
        self.add_widget(layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def iniciar_leitura_qr_sequencial(self, instance):
        if has_android:
            try:
                def callback(permissions, results):
                    if all(results):
                        Popup(title='Câmera Ativa',
                              content=Label(text='Permissão concedida! Iniciando scanner de QR...'),
                              size_hint=(0.8, 0.3)).open()
                    else:
                        Popup(title='Permissão Negada',
                              content=Label(text='A permissão de câmera é necessária para ler o QR Code.'),
                              size_hint=(0.8, 0.3)).open()

                request_permissions([Permission.CAMERA], callback)
            except Exception as e:
                Popup(title='Aviso', content=Label(text=f'Erro ao abrir câmera: {str(e)}'), size_hint=(0.8, 0.3)).open()
        else:
            Popup(title='Simulador PC', content=Label(
                text='A câmera do celular não pode ser aberta diretamente no Windows. Teste no Android!'),
                  size_hint=(0.8, 0.3)).open()

    def checar_dados_qr(self, instance):
        Popup(title='Checagem', content=Label(text='Checando dados dos QR Codes capturados...'),
              size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

        # ==========================================
        # 8. TELA DE CHECAGEM (DUPLO QR CODE / SCAN)
        # ==========================================
        class ChecagemScreen(Screen):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.main_layout = BoxLayout(orientation='vertical')

                with self.main_layout.canvas.before:
                    self.bg_color = Color(0.96, 0.93, 0.88, 1)
                    self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
                self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

                # Cabeçalho
                header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 5])
                with header.canvas.before:
                    Color(0.12, 0.14, 0.18, 1)
                    self.header_bg = Rectangle(size=header.size, pos=header.size)
                header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                            pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

                header.add_widget(
                    Label(text='CHECAGEM DE QR CODE', color=(1.0, 0.82, 0.0, 1), font_size='15sp', bold=True,
                          halign='center'))
                self.main_layout.add_widget(header)

                scroll = ScrollView(size_hint=(1, 1))
                content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=20)
                content.bind(minimum_height=content.setter('height'))

                # --- PRIMEIRO BLOCO (QR CODE 1) ---
                lbl_bloco1 = Label(text='Primeira Leitura', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True,
                                   size_hint_y=None, height='20dp', halign='left')
                lbl_bloco1.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
                content.add_widget(lbl_bloco1)

                self.btn_scan_1 = RoundedButton(text='📷 Escanear QR Code 1', bg_color=(0.25, 0.65, 0.85, 1),
                                                size_hint_y=None, height='45dp')
                self.btn_scan_1.color = (1, 1, 1, 1);
                self.btn_scan_1.bold = True;
                self.btn_scan_1.font_size = '12sp'
                self.btn_scan_1.bind(on_release=lambda x: self.abrir_scanner(1))
                content.add_widget(self.btn_scan_1)

                self.input_resultado_1 = TextInput(
                    text='', hint_text='O código 1 aparecerá aqui...', multiline=False,
                    font_size='12sp', size_hint_y=None, height='42dp', halign='center'
                )
                content.add_widget(self.input_resultado_1)

                # --- SEGUNDO BLOCO (QR CODE 2) ---
                lbl_bloco2 = Label(text='Segunda Leitura', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True,
                                   size_hint_y=None, height='20dp', halign='left')
                lbl_bloco2.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
                content.add_widget(lbl_bloco2)

                self.btn_scan_2 = RoundedButton(text='📷 Escanear QR Code 2', bg_color=(0.25, 0.65, 0.85, 1),
                                                size_hint_y=None, height='45dp')
                self.btn_scan_2.color = (1, 1, 1, 1);
                self.btn_scan_2.bold = True;
                self.btn_scan_2.font_size = '12sp'
                self.btn_scan_2.bind(on_release=lambda x: self.abrir_scanner(2))
                content.add_widget(self.btn_scan_2)

                self.input_resultado_2 = TextInput(
                    text='', hint_text='O código 2 aparecerá aqui...', multiline=False,
                    font_size='12sp', size_hint_y=None, height='42dp', halign='center'
                )
                content.add_widget(self.input_resultado_2)

                # --- BOTÃO CHECAR ---
                btn_checar = RoundedButton(text='✅ CHECAR', bg_color=(0.25, 0.7, 0.4, 1), size_hint_y=None,
                                           height='50dp')
                btn_checar.color = (1, 1, 1, 1);
                btn_checar.bold = True;
                btn_checar.font_size = '14sp'
                btn_checar.bind(on_release=self.realizar_checagem)
                content.add_widget(btn_checar)

                scroll.add_widget(content)
                self.main_layout.add_widget(scroll)
                self.main_layout.add_widget(CriarBarraNavegacao(ativa='inicio'))
                self.add_widget(self.main_layout)

            def on_enter(self):
                paleta = obter_paleta_atual()
                self.bg_color.rgba = paleta['bg']

            def abrir_scanner(self, qual_botao):
                if platform == 'android':
                    try:
                        from jnius import autoclass
                        Intent = autoclass('android.content.Intent')
                        intent = Intent("com.google.zxing.client.android.SCAN")
                        intent.putExtra("SCAN_MODE", "QR_CODE_MODE")
                        PythonActivity = autoclass('org.kivy.android.PythonActivity')
                        activity = PythonActivity.mActivity
                        activity.startActivityForResult(intent, qual_botao)
                    except Exception as e:
                        if qual_botao == 1:
                            self.input_resultado_1.text = f"Erro: {e}"
                        else:
                            self.input_resultado_2.text = f"Erro: {e}"
                else:
                    # Simulador para testes no PC
                    if qual_botao == 1:
                        self.input_resultado_1.text = "QR_TESTE_CHICOTE_A"
                    else:
                        self.input_resultado_2.text = "QR_TESTE_CHICOTE_B"

                    Popup(
                        title=f'Simulador QR Code {qual_botao}',
                        content=Label(text=f'Código {qual_botao} simulado com sucesso no PC!'),
                        size_hint=(0.8, 0.3)
                    ).open()

            def realizar_checagem(self, instance):
                c1 = self.input_resultado_1.text.strip()
                c2 = self.input_resultado_2.text.strip()

                if not c1 or not c2:
                    msg = "Por favor, preencha ou escaneie os dois códigos antes de checar!"
                else:
                    msg = f"Checagem realizada com sucesso!\nCódigo 1: {c1}\nCódigo 2: {c2}"

                Popup(title='Resultado da Checagem', content=Label(text=msg), size_hint=(0.8, 0.3)).open()

            def _update_bg(self, instance, value):
                self.bg_rect.size = instance.size
                self.bg_rect.pos = instance.pos


# ==========================================
# 8. TELA DE CHECAGEM (DUPLO QR CODE / SCAN)
# ==========================================
class ChecagemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')

        with self.main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Cabeçalho
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 5])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

        header.add_widget(
            Label(text='CHECAGEM DE QR CODE', color=(1.0, 0.82, 0.0, 1), font_size='15sp', bold=True, halign='center'))
        self.main_layout.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=20)
        content.bind(minimum_height=content.setter('height'))

        # --- PRIMEIRO BLOCO (QR CODE 1) ---
        lbl_bloco1 = Label(text='Primeira Leitura', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True,
                           size_hint_y=None, height='20dp', halign='left')
        lbl_bloco1.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_bloco1)

        self.btn_scan_1 = RoundedButton(text='📷 Escanear QR Code 1', bg_color=(0.25, 0.65, 0.85, 1), size_hint_y=None,
                                        height='45dp')
        self.btn_scan_1.color = (1, 1, 1, 1);
        self.btn_scan_1.bold = True;
        self.btn_scan_1.font_size = '12sp'
        self.btn_scan_1.bind(on_release=lambda x: self.abrir_scanner(1))
        content.add_widget(self.btn_scan_1)

        self.input_resultado_1 = TextInput(
            text='', hint_text='O código 1 aparecerá aqui...', multiline=False,
            font_size='12sp', size_hint_y=None, height='42dp', halign='center'
        )
        content.add_widget(self.input_resultado_1)

        # --- SEGUNDO BLOCO (QR CODE 2) ---
        lbl_bloco2 = Label(text='Segunda Leitura', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True,
                           size_hint_y=None, height='20dp', halign='left')
        lbl_bloco2.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_bloco2)

        self.btn_scan_2 = RoundedButton(text='📷 Escanear QR Code 2', bg_color=(0.25, 0.65, 0.85, 1), size_hint_y=None,
                                        height='45dp')
        self.btn_scan_2.color = (1, 1, 1, 1);
        self.btn_scan_2.bold = True;
        self.btn_scan_2.font_size = '12sp'
        self.btn_scan_2.bind(on_release=lambda x: self.abrir_scanner(2))
        content.add_widget(self.btn_scan_2)

        self.input_resultado_2 = TextInput(
            text='', hint_text='O código 2 aparecerá aqui...', multiline=False,
            font_size='12sp', size_hint_y=None, height='42dp', halign='center'
        )
        content.add_widget(self.input_resultado_2)

        # --- BOTÃO CHECAR ---
        btn_checar = RoundedButton(text='✅ CHECAR', bg_color=(0.25, 0.7, 0.4, 1), size_hint_y=None, height='50dp')
        btn_checar.color = (1, 1, 1, 1);
        btn_checar.bold = True;
        btn_checar.font_size = '14sp'
        btn_checar.bind(on_release=self.realizar_checagem)
        content.add_widget(btn_checar)

        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='inicio'))
        self.add_widget(self.main_layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def abrir_scanner(self, qual_botao):
        if platform == 'android':
            try:
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                intent = Intent("com.google.zxing.client.android.SCAN")
                intent.putExtra("SCAN_MODE", "QR_CODE_MODE")
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                activity.startActivityForResult(intent, qual_botao)
            except Exception as e:
                if qual_botao == 1:
                    self.input_resultado_1.text = f"Erro: {e}"
                else:
                    self.input_resultado_2.text = f"Erro: {e}"
        else:
            # Simulador para testes no PC
            if qual_botao == 1:
                self.input_resultado_1.text = "QR_TESTE_CHICOTE_A"
            else:
                self.input_resultado_2.text = "QR_TESTE_CHICOTE_B"

            Popup(
                title=f'Simulador QR Code {qual_botao}',
                content=Label(text=f'Código {qual_botao} simulado com sucesso no PC!'),
                size_hint=(0.8, 0.3)
            ).open()

    def realizar_checagem(self, instance):
        c1 = self.input_resultado_1.text.strip()
        c2 = self.input_resultado_2.text.strip()

        if not c1 or not c2:
            msg = "Por favor, preencha ou escaneie os dois códigos antes de checar!"
        else:
            msg = f"Checagem realizada com sucesso!\nCódigo 1: {c1}\nCódigo 2: {c2}"

        Popup(title='Resultado da Checagem', content=Label(text=msg), size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos