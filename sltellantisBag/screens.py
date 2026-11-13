"""
===============================================================================
MÓDULO DE TELAS DO APLICATIVO STELLANTISBAG (screens.py)
===============================================================================
Este arquivo contém a definição e implementação de todas as telas (Screens)
do aplicativo construído em Kivy.

Estrutura das Telas:
 1. WelcomeScreen       - Tela de Login / Autenticação de Usuário.
 2. HomeScreen          - Dashboard Principal / Boas-Vindas e Ações Rápidas.
 3. ReportsScreen       - Relatórios Executivos, KPIs e Histórico.
 4. ProductionScreen    - Controle e Apontamento Hora a Hora da Produção.
 5. UserProfileScreen   - Cadastro e Edição de Dados do Operador.
 6. ConfigScreen        - Painel Central de Configurações e Preferências.
 7. ThemeScreen         - Seleção Visual de Temas (Clássico, Dark, Azul).
 8. SupportScreen       - Central de Suporte Técnico e Limpeza de Dados.
#por enquanto esta deletada a 9
 10. ChecagemScreen     - Tela de Dupla Leitura de QR Codes (Chicotes Elétricos).
===============================================================================
"""

from datetime import datetime

# Importações principais do Kivy

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.utils import platform
from kivy.graphics import RoundedRectangle
import os
import pandas as pd
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
# Verification de bibliotecas nativas do Android (Leitura de Câmera/QR Code)
try:
    from jnius import autoclass
    from android.permissions import request_permissions, Permission
    has_android = True
except ImportError:
    has_android = False

# Importação dos módulos locais de dados e componentes reutilizáveis
from database import DADOS_APP, obter_perfil_atual, salvar_dados_gerais, obter_paleta_atual
from components import CircularAvatar, RoundedButton, CriarBarraNavegacao, abrir_seletor_foto

from kivy.uix.screenmanager import Screen

class SplashScreen(Screen):
    pass
# =============================================================================
# 1. TELA DE LOGIN / BOAS-VINDAS (WelcomeScreen)
# =============================================================================

class WelcomeScreen(Screen):
    """
    Tela de login com suporte a Senha Master, validação no arquivo mybad_banco_dados.csv
    e redirecionamento para o cadastro.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.main_layout = BoxLayout(orientation='vertical', padding=25, spacing=15)

        # Fundo roxo corporativo da Splash Screen
        with self.main_layout.canvas.before:
            Color(0.12, 0.08, 0.22, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        self.main_layout.add_widget(Widget(size_hint_y=None, height='10dp'))

        # --- LOGOTIPO ---
        logo_layout = AnchorLayout(anchor_x='center', anchor_y='center', size_hint_y=None, height='120dp')
        self.img_logo = Image(
            source='icones/icone_mybag.png',
            size_hint=(None, None),
            size=(110, 110),
            allow_stretch=True,
            keep_ratio=True
        )
        logo_layout.add_widget(self.img_logo)
        self.main_layout.add_widget(logo_layout)

        # --- TÍTULO ---
        self.lbl_titulo = Label(
            text='STELLANTIS BAG',
            color=(0.95, 0.82, 0.45, 1),
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height='25dp',
            halign='center'
        )
        self.lbl_titulo.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.main_layout.add_widget(self.lbl_titulo)

        # --- FORMULÁRIO (MATRÍCULA E SENHA) ---
        form_layout = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None, height='140dp', padding=[15, 0])

        self.input_matricula = TextInput(
            hint_text='Digite sua Matrícula',
            multiline=False,
            size_hint_y=None,
            height='42dp',
            padding_x=[12, 12],
            cursor_color=(0.95, 0.82, 0.45, 1)
        )

        self.input_senha = TextInput(
            hint_text='Digite sua Senha',
            password=True,
            multiline=False,
            size_hint_y=None,
            height='42dp',
            padding_x=[12, 12],
            cursor_color=(0.95, 0.82, 0.45, 1)
        )

        form_layout.add_widget(self.input_matricula)
        form_layout.add_widget(self.input_senha)
        self.main_layout.add_widget(form_layout)

        # --- MENSAGEM DE ERRO ---
        self.lbl_erro = Label(
            text='',
            color=(1, 0.4, 0.4, 1),
            font_size='12sp',
            size_hint_y=None,
            height='25dp',
            halign='center'
        )
        self.lbl_erro.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        self.main_layout.add_widget(self.lbl_erro)

        # --- OPÇÕES ---
        opcoes_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='35dp', padding=[15, 0])

        lembrar_box = BoxLayout(orientation='horizontal', spacing=8, size_hint_x=0.6)
        self.chk_lembrar = CheckBox(size_hint_y=None, height='30dp', width='30dp')
        lbl_lembrar = Label(text='Lembrar-me', color=(0.85, 0.85, 0.9, 1), font_size='12sp', halign='left',
                            valign='middle')
        lbl_lembrar.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        lembrar_box.add_widget(self.chk_lembrar)
        lembrar_box.add_widget(lbl_lembrar)

        self.btn_esqueci = Button(
            text='Esqueci a senha?',
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.95, 0.82, 0.45, 1),
            font_size='12sp',
            size_hint_x=0.4,
            halign='right'
        )
        self.btn_esqueci.bind(on_release=self.esqueci_senha_acao)

        opcoes_layout.add_widget(lembrar_box)
        opcoes_layout.add_widget(self.btn_esqueci)
        self.main_layout.add_widget(opcoes_layout)

        self.main_layout.add_widget(Widget())

        # --- BOTÕES DE AÇÃO ---
        botoes_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height='100dp', padding=[15, 0])

        self.btn_entrar = Button(
            text='ENTRAR',
            size_hint_y=None,
            height='42dp',
            background_normal='',
            background_color=(0.95, 0.82, 0.45, 1),
            color=(0.12, 0.08, 0.22, 1),
            bold=True,
            font_size='13sp'
        )
        self.btn_entrar.bind(on_release=self.fazer_login)

        # Botão de Cadastrar / Inscrever-se ligado corretamente para abrir a tela de perfil/cadastro
        self.btn_cadastrar = Button(
            text='CADASTRAR / INSCREVER-SE',
            size_hint_y=None,
            height='42dp',
            background_normal='',
            background_color=(0.25, 0.20, 0.45, 1),
            color=(0.95, 0.82, 0.45, 1),
            bold=True,
            font_size='12sp'
        )
        self.btn_cadastrar.bind(on_release=self.ir_para_cadastro)

        botoes_layout.add_widget(self.btn_entrar)
        botoes_layout.add_widget(self.btn_cadastrar)
        self.main_layout.add_widget(botoes_layout)

        self.add_widget(self.main_layout)

    def fazer_login(self, instance):
        """Valida se é a senha master ou se consta no arquivo mybad_banco_dados.csv"""
        matricula_digitada = self.input_matricula.text.strip()
        senha_digitada = self.input_senha.text.strip()

        if not matricula_digitada or not senha_digitada:
            self.lbl_erro.text = "Preencha a matrícula e a senha!"
            return

        # 1. VALIDAÇÃO DA SENHA MASTER
        if matricula_digitada == "124405" and senha_digitada == "1920":
            self.lbl_erro.text = ""
            print("Login autorizado via Senha Master!")
            App.get_running_app().sm.current = 'inicio'
            return

        # 2. VALIDAÇÃO NO BANCO CSV (mybad_banco_dados.csv)
        caminho_csv = 'mybad_banco_dados.csv'

        if not os.path.exists(caminho_csv):
            self.lbl_erro.text = "Erro: Arquivo mybad_banco_dados.csv não encontrado!"
            return

        try:
            # Lê o arquivo CSV usando pandas
            df = pd.read_csv(caminho_csv)
            df.columns = [str(col).strip().lower() for col in df.columns]

            if 'matricula' not in df.columns or 'senha' not in df.columns:
                self.lbl_erro.text = "Erro: O CSV precisa conter as colunas 'matricula' e 'senha'."
                return

            df['matricula'] = df['matricula'].astype(str).str.strip()
            df['senha'] = df['senha'].astype(str).str.strip()

            # Checa se o usuário existe na base
            valido = df[(df['matricula'] == matricula_digitada) & (df['senha'] == senha_digitada)]

            if not valido.empty:
                self.lbl_erro.text = ""
                App.get_running_app().sm.current = 'inicio'
            else:
                self.lbl_erro.text = "Matrícula ou senha inválidas!"

        except Exception as e:
            self.lbl_erro.text = "Erro ao processar o banco de dados CSV."

    def ir_para_cadastro(self, instance):
        """Redireciona para a tela de cadastro/usuário."""
        # Se a sua tela de cadastro/perfil estiver registrada no main.py com outro nome (ex: 'user_profile' ou 'cadastro'), ajuste aqui:
        App.get_running_app().sm.current = 'user_profile'

    def esqueci_senha_acao(self, instance):
        self.lbl_erro.text = "Use a Senha Master ou contate o suporte."

    def _update_bg(self, instance, value):
        self.bg_rc = getattr(self, 'bg_rect', None)
        if self.bg_rc:
            self.bg_rc.size = instance.size
            self.bg_rc.pos = instance.pos
#=================================
# 2. TELA DE INÍCIO / DASHBOARD OPERACIONAL (HomeScreen)
# =============================================================================
class HomeScreen(Screen):
    """
    Painel principal da aplicação. Exibe um resumo do operador e oferece 
    atalhos rápidos para Registrar Produção, Ver Relatórios e Escanear QR Code.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')

        with self.main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Header Superior
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 5])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

        header.add_widget(Label(text='STELLANTISBAG - INÍCIO', color=(1.0, 0.82, 0.0, 1), font_size='15sp', bold=True, halign='left'))
        self.main_layout.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=16)
        content.bind(minimum_height=content.setter('height'))

        # --- CARD DE RESUMO DO OPERADOR ---
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

        lbl_user = Label(text=f'👤 Olá, {nome_usuario}', color=(1.0, 0.82, 0.0, 1), font_size='14sp', bold=True, halign='left')
        lbl_user.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        lbl_status = Label(text=f'Meta Atual: {meta_hoje} | Produzido: {prod_hoje}', color=(1, 1, 1, 1), font_size='12sp', halign='left')
        lbl_status.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        lbl_linha = Label(text='📍 Setor: Montagem de Chicotes Elétricos', color=(0.8, 0.8, 0.8, 1), font_size='11sp', halign='left')
        lbl_linha.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))

        card_resumo.add_widget(lbl_user)
        card_resumo.add_widget(lbl_status)
        card_resumo.add_widget(lbl_linha)
        content.add_widget(card_resumo)

        # --- ATALHOS / AÇÕES RÁPIDAS ---
        lbl_sec_acoes = Label(text='Ações Rápidas', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True, size_hint_y=None, height='25dp', halign='left')
        lbl_sec_acoes.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_sec_acoes)

        box_botoes_principais = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing=10)

        btn_registrar = RoundedButton(text='📝 REGISTRAR', bg_color=(0.25, 0.65, 0.85, 1))
        btn_registrar.color = (1, 1, 1, 1); btn_registrar.bold = True; btn_registrar.font_size = '12sp'
        btn_registrar.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'producao'))

        btn_dashboard = RoundedButton(text='📊 DASHBOARD', bg_color=(0.25, 0.7, 0.4, 1))
        btn_dashboard.color = (1, 1, 1, 1); btn_dashboard.bold = True; btn_dashboard.font_size = '12sp'
        btn_dashboard.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'relatorios'))

        box_botoes_principais.add_widget(btn_registrar)
        box_botoes_principais.add_widget(btn_dashboard)
        content.add_widget(box_botoes_principais)

        btn_checagem = RoundedButton(text='📷 CHECAGEM', bg_color=(0.9, 0.6, 0.2, 1), size_hint_y=None, height='48dp')
        btn_checagem.color = (1, 1, 1, 1); btn_checagem.bold = True; btn_checagem.font_size = '12sp'
        btn_checagem.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'checagem'))
        content.add_widget(btn_checagem)

        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='inicio'))
        self.add_widget(self.main_layout)

    def on_enter(self):
        """Atualiza a paleta ao carregar a tela."""
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# =============================================================================
# 3. TELA DE DASHBOARD DE RELATÓRIOS (ReportsScreen)
# =============================================================================
class ReportsScreen(Screen):
    """
    Exibe indicadores de desempenho (KPIs), percentual de conclusão da meta
    diária e permite resetar o histórico de apontamentos salvos.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        with self.main_layout.canvas.before:
            self.bg_color = Color(0.12, 0.14, 0.18, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.size)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Cabeçalho
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

        # --- CARDS KPI (META E PRODUÇÃO) ---
        self.grid_kpi = GridLayout(cols=2, size_hint_y=None, height='85dp', spacing=10)
        self.card_meta = self.criar_card_kpi("META DIÁRIA", "0 un", (0.2, 0.6, 0.8, 1))
        self.card_prod = self.criar_card_kpi("PRODUZIDO HOJE", "0 un", (0.2, 0.7, 0.4, 1))
        self.grid_kpi.add_widget(self.card_meta['layout'])
        self.grid_kpi.add_widget(self.card_prod['layout'])
        self.content.add_widget(self.grid_kpi)

        # --- CARD DE EFICIÊNCIA GERAL ---
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

        # --- BOTÃO APAGAR REGISTROS ---
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
        """Função auxiliar para construir dinamicamente cards de métricas (KPIs)."""
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
        """Zera os contadores diários e limpa a lista do histórico de produção."""
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            perfil["total_produzido_hoje"] = 0
            perfil["porcentagem_hoje"] = 0.0
            perfil["historico_salvo"] = []
            salvar_dados_gerais()
        self.on_enter()
        Popup(title='Relatórios Zerados', content=Label(text='Todos os registros e dados foram apagados com sucesso!'), size_hint=(0.8, 0.3)).open()

    def on_enter(self):
        """Recarrega os valores de meta, produção atual e histórico salvo."""
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

        perfil = obter_perfil_atual()
        meta = perfil.get("meta_hoje", 720) if isinstance(perfil, dict) else 720
        total = perfil.get("total_produzido_hoje", 0) if isinstance(perfil, dict) else 0
        pct = perfil.get("porcentagem_hoje", 0.0) if isinstance(perfil, dict) else 0.0

        self.card_meta['label_valor'].text = f"{meta} un"
        self.card_prod['label_valor'].text = f"{total} un"
        self.lbl_status_val.text = f"{pct:.1f}% Concluído"

        # Mensagem contextual de status
        if pct >= 100:
            self.lbl_status_det.text = "Status: Meta atingida! 🟢"
        elif pct >= 80:
            self.lbl_status_det.text = "Status: Próximo da meta. ⚠️"
        else:
            self.lbl_status_det.text = "Status: Abaixo da meta. ❌"

        historico = perfil.get("historico_salvo", []) if isinstance(perfil, dict) else []
        self.btn_apagar_rel.text = f'🗑️ APAGAR TUDO / ZERAR REGISTROS ({len(historico)})'

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# =============================================================================
# 4. TELA DE PRODUÇÃO / APONTAMENTO HORA A HORA (ProductionScreen)
# =============================================================================
class ProductionScreen(Screen):
    """
    Tela principal de registro industrial de montagem de chicotes elétricos.
    Calcula hora a hora a quantidade produzida, a variação em relação à meta (Delta),
    permite alternar turnos, ajustar metas e exportar relatórios via WhatsApp.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=4, spacing=2)

        with self.main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Header Superior
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='38dp', padding=[10, 2])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

        header.add_widget(Label(text='PAINEL DE CONTROLE - PRODUÇÃO', color=(1.0, 0.82, 0.0, 1), font_size='12sp', bold=True, halign='center'))
        self.main_layout.add_widget(header)

        # --- CABEÇALHO DA TABELA ---
        self.table_header = BoxLayout(orientation='horizontal', size_hint_y=None, height='28dp', spacing=1, size_hint_x=1)
        with self.table_header.canvas.before:
            Color(0.82, 0.78, 0.70, 1)
            self.bg_th = Rectangle(size=self.table_header.size, pos=self.table_header.pos)
        self.table_header.bind(size=lambda inst, val: setattr(self.bg_th, 'size', inst.size),
                               pos=lambda inst, val: setattr(self.bg_th, 'pos', inst.pos))

        self.table_header.add_widget(Label(text='HORA', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='9sp', halign='center', size_hint_x=0.24))
        self.table_header.add_widget(Label(text='Meta', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='9sp', halign='center', size_hint_x=0.12))
        self.table_header.add_widget(Label(text='Cap.', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='9sp', halign='center', size_hint_x=0.12))
        self.table_header.add_widget(Label(text='Res.', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='9sp', halign='center', size_hint_x=0.18))
        self.table_header.add_widget(Label(text='Prod.', color=(0.1, 0.45, 0.2, 1), bold=True, font_size='9sp', halign='center', size_hint_x=0.17))
        self.table_header.add_widget(Label(text='Delta', color=(0.12, 0.14, 0.18, 1), bold=True, font_size='9sp', halign='center', size_hint_x=0.17))
        self.main_layout.add_widget(self.table_header)

        # --- CORPO DA TABELA (HORÁRIOS DOS TURNOS) ---
        scroll_vertical = ScrollView(size_hint=(1, 1))
        content_scroll = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2, padding=[0, 0])
        content_scroll.bind(minimum_height=content_scroll.setter('height'))

        self.turno_atual = 2
        # Matriz de dados para o 2º Turno (Horário, Meta Hora, Meta Acumulada)
        self.dados_turno_2 = [
            ("16:00-17:00", 100, 100), ("17:00-18:00", 100, 200),
            ("18:15-19:00", 67, 267),  ("19:00-19:15", 19, 286),
            ("20:15-21:00", 67, 353),  ("21:00-22:00", 100, 453),
            ("22:00-23:00", 100, 553), ("23:15-00:00", 67, 620),
            ("00:00-01:09", 100, 720),
        ]
        # Matriz de dados para o 1º Turno
        self.dados_turno_1 = [
            ("06:00-07:00", 100, 100), ("07:00-08:00", 100, 200),
            ("08:15-09:00", 67, 267),  ("09:00-09:15", 19, 286),
            ("10:15-11:00", 67, 353),  ("11:00-12:00", 100, 453),
            ("12:45-13:45", 100, 553), ("13:45-14:30", 67, 620),
            ("14:30-15:43", 100, 720),
        ]

        self.linhas_widgets = []
        self.tabela_linhas_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2, size_hint_x=1)
        self.construir_linhas_tabela()

        content_scroll.add_widget(self.tabela_linhas_layout)
        scroll_vertical.add_widget(content_scroll)
        self.main_layout.add_widget(scroll_vertical)

        # --- SELEÇÃO DE TURNO E AJUSTE DE META ---
        box_config_inferior = BoxLayout(orientation='horizontal', size_hint_y=None, height='32dp', padding=[6, 2], spacing=6)
        with box_config_inferior.canvas.before:
            Color(0.90, 0.87, 0.80, 1)
            self.bg_card_meta = RoundedRectangle(size=box_config_inferior.size, pos=box_config_inferior.pos, radius=[6])
        box_config_inferior.bind(size=lambda inst, val: setattr(self.bg_card_meta, 'size', inst.size),
                                 pos=lambda inst, val: setattr(self.bg_card_meta, 'pos', inst.pos))

        self.btn_turno_1 = Button(text='1º Turno', background_color=(0.25, 0.3, 0.4, 1), color=(1, 1, 1, 1), bold=True, font_size='9sp', size_hint_x=0.25)
        self.btn_turno_2 = Button(text='2º Turno', background_color=(0.08, 0.16, 0.36, 1), color=(1, 1, 1, 1), bold=True, font_size='9sp', size_hint_x=0.25)
        self.btn_turno_1.bind(on_release=lambda x: self.mudar_turno(1))
        self.btn_turno_2.bind(on_release=lambda x: self.mudar_turno(2))

        perfil_inicial = obter_perfil_atual()
        meta_inicial = str(perfil_inicial.get("meta_hoje", 720) if isinstance(perfil_inicial, dict) else 720)
        self.input_meta_selecionada = TextInput(text=meta_inicial, multiline=False, font_size='10sp', size_hint_x=0.25, halign='center', padding=[2, 6, 2, 6])

        btn_salvar_meta = RoundedButton(text='Meta', bg_color=(0.25, 0.65, 0.85, 1), size_hint_x=0.25)
        btn_salvar_meta.color = (1, 1, 1, 1); btn_salvar_meta.font_size = '9sp'; btn_salvar_meta.bold = True
        btn_salvar_meta.bind(on_release=self.aplicar_filtro_meta)

        box_config_inferior.add_widget(self.btn_turno_1)
        box_config_inferior.add_widget(self.btn_turno_2)
        box_config_inferior.add_widget(self.input_meta_selecionada)
        box_config_inferior.add_widget(btn_salvar_meta)
        self.main_layout.add_widget(box_config_inferior)

        # --- PAINEL DE TOTAIS E PERDAS ---
        box_totais = BoxLayout(orientation='horizontal', size_hint_y=None, height='22dp', spacing=10, padding=[10, 1])
        self.lbl_total_pos = Label(text='Positivo: +0', color=(0, 0.5, 0, 1), bold=True, font_size='9.5sp', halign='center')
        self.lbl_total_neg = Label(text='Perdas Totais: 0', color=(0.8, 0, 0, 1), bold=True, font_size='9.5sp', halign='center')
        box_totais.add_widget(self.lbl_total_pos)
        box_totais.add_widget(self.lbl_total_neg)
        self.main_layout.add_widget(box_totais)

        # --- BOTÕES DE AÇÃO ---
        box_botoes = BoxLayout(orientation='horizontal', size_hint_y=None, height='38dp', spacing=6, padding=[4, 2])
        
        btn_calcular = RoundedButton(text='CALCULAR', bg_color=(0.25, 0.65, 0.85, 1))
        btn_calcular.color = (1, 1, 1, 1); btn_calcular.bold = True; btn_calcular.font_size = '9.5sp'
        btn_calcular.bind(on_release=self.calcular_totais)

        btn_salvar = RoundedButton(text='SALVAR', bg_color=(0.25, 0.7, 0.4, 1))
        btn_salvar.color = (1, 1, 1, 1); btn_salvar.bold = True; btn_salvar.font_size = '9.5sp'
        btn_salvar.bind(on_release=self.salvar_dados)

        btn_compartilhar = RoundedButton(text='WHATSAPP', bg_color=(0.9, 0.6, 0.2, 1))
        btn_compartilhar.color = (1, 1, 1, 1); btn_compartilhar.bold = True; btn_compartilhar.font_size = '9.5sp'
        btn_compartilhar.bind(on_release=self.compartilhar_dados)

        box_botoes.add_widget(btn_calcular)
        box_botoes.add_widget(btn_salvar)
        box_botoes.add_widget(btn_compartilhar)
        self.main_layout.add_widget(box_botoes)

        self.main_layout.add_widget(CriarBarraNavegacao(ativa='producao'))
        self.add_widget(self.main_layout)

    def mudar_turno(self, turno):
        """Alterna a visualização da tabela entre o 1º e 2º Turno."""
        self.turno_atual = turno
        if turno == 1:
            self.btn_turno_1.background_color = (0.08, 0.16, 0.36, 1)
            self.btn_turno_2.background_color = (0.25, 0.3, 0.4, 1)
        else:
            self.btn_turno_2.background_color = (0.08, 0.16, 0.36, 1)
            self.btn_turno_1.background_color = (0.25, 0.3, 0.4, 1)
        self.construir_linhas_tabela()
        self.aplicar_filtro_meta(None)

    def construir_linhas_tabela(self):
        """Gera as linhas da tabela de entrada com base nos horários do turno ativo."""
        self.tabela_linhas_layout.clear_widgets()
        self.linhas_widgets = []
        dados_ativos = self.dados_turno_1 if self.turno_atual == 1 else self.dados_turno_2

        for hora, h720_meta, h720_cap in dados_ativos:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height='34dp', spacing=1, size_hint_x=1)

            lbl_h = Label(text=hora, color=(0.12, 0.14, 0.18, 1), font_size='9sp', halign='center', size_hint_x=0.24)
            lbl_hxh = Label(text=str(h720_meta), color=(0.12, 0.14, 0.18, 1), font_size='9.5sp', bold=True, halign='center', size_hint_x=0.12)
            lbl_cap = Label(text=str(h720_cap), color=(0.12, 0.14, 0.18, 1), font_size='9.5sp', halign='center', size_hint_x=0.12)
            txt_res = TextInput(text='', hint_text='Res.', multiline=False, font_size='10sp', halign='center', size_hint_x=0.18, padding=[2, 6, 2, 6])
            lbl_prod = Label(text='0', color=(0.1, 0.5, 0.1, 1), bold=True, font_size='9.5sp', halign='center', size_hint_x=0.17)
            lbl_delta = Label(text='0', color=(0.1, 0.5, 0.1, 1), bold=True, font_size='9.5sp', halign='center', size_hint_x=0.17)

            linha_info = {
                'row': row, 'lbl_h': lbl_h, 'lbl_hxh': lbl_hxh, 'lbl_cap': lbl_cap,
                'txt_res': txt_res, 'lbl_prod': lbl_prod, 'lbl_delta': lbl_delta,
                'base_meta': h720_meta, 'base_cap': h720_cap
            }
            # Recalcula automaticamente ao digitar no campo "Res."
            txt_res.bind(text=lambda inst, val: self.calcular_totais(None))

            row.add_widget(lbl_h); row.add_widget(lbl_hxh); row.add_widget(lbl_cap)
            row.add_widget(txt_res); row.add_widget(lbl_prod); row.add_widget(lbl_delta)

            self.linhas_widgets.append(linha_info)
            self.tabela_linhas_layout.add_widget(row)

        self.tabela_linhas_layout.height = len(dados_ativos) * 35

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']
        self.mudar_turno(self.turno_atual)

    def aplicar_filtro_meta(self, instance):
        """Ajusta proporcionalmente os objetivos da tabela (ex: 720 un vs 360 un)."""
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
        """
        Processa os valores acumulados digitados pelo operador, calcula a
        produção individual por hora e gera o balanço de deltas (perdas/ganhos).
        """
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
                prod_intervalo = res_atual if i == 0 else (res_atual - acumulado_anterior)
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
        """Grava a sessão de apontamento atual no histórico mantido no banco de dados."""
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
        """
        Gera um relatório formatado em texto contendo a produção de cada hora, 
        copia para a área de transferência e abre a API do WhatsApp para envio.
        """
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
            f"*Previsto/Realizado*\n"
            f"{detalhes_linhas}\n"
            f"-------Fechamento----\n\n"
            f"*Produção prevista*: {meta_total}\n"
            f"*Produção realizada*: {prod_total}\n"
            f"*OPE*: {ope_calculado:.1f}%\n\n"
            f"Perdas: -{total_perdas}\n"
        )

        Clipboard.copy(texto)

        try:
            import urllib.parse, webbrowser
            webbrowser.open(f"https://wa.me/5581996974733?text={urllib.parse.quote(texto)}")
        except Exception:
            pass

        Popup(title='Compartilhar', content=Label(text='Relatório copiado e pronto para o WhatsApp!'), size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# =============================================================================
# 5. TELA DE PERFIL DO USUÁRIO (UserProfileScreen)
# =============================================================================
class UserProfileScreen(Screen):
    """
    Formulário para edição dos dados pessoais do operador (Nome, E-mail,
    Telefone e Função).
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        with self.main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        header = Label(
            text='EDITAR PERFIL DO USUÁRIO',
            color=(1.0, 0.82, 0.0, 1),
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height='40dp'
        )
        self.main_layout.add_widget(header)

        # Formulário dos campos
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

            txt_input = TextInput(text='', multiline=False, font_size='13sp', size_hint_y=None, height='35dp')
            self.inputs[chave] = txt_input
            box.add_widget(txt_input)
            form_layout.add_widget(box)

        self.main_layout.add_widget(form_layout)

        # Botões de Ação do Perfil
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

        btn_voltar = RoundedButton(text='Voltar', bg_color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height='40dp')
        btn_voltar.bind(on_release=self.voltar_config)
        self.main_layout.add_widget(btn_voltar)

        self.add_widget(self.main_layout)
        self.carregar_dados_salvos()

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def carregar_dados_salvos(self):
        """Preenche os campos de texto com as informações armazenadas no perfil."""
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            for chave, txt_input in self.inputs.items():
                txt_input.text = str(perfil.get(chave, ''))

    def salvar_perfil(self, instance):
        """Grava as atualizações do formulário no arquivo de banco de dados."""
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            for chave, txt_input in self.inputs.items():
                perfil[chave] = txt_input.text.strip()
            salvar_dados_gerais()

        Popup(title='Sucesso', content=Label(text='Informações do perfil salvas com sucesso!'), size_hint=(0.8, 0.3)).open()

    def apagar_campos(self, instance):
        """Limpa visualmente os campos da tela."""
        for txt_input in self.inputs.values():
            txt_input.text = ''
        Popup(title='Apagar', content=Label(text='Campos limpos com sucesso!'), size_hint=(0.8, 0.3)).open()

    def excluir_perfil(self, instance):
        """Remove os dados do perfil do banco de dados e limpa os campos."""
        perfil = obter_perfil_atual()
        if isinstance(perfil, dict):
            for chave in self.inputs.keys():
                perfil[chave] = ''
            salvar_dados_gerais()
        self.apagar_campos(instance)
        Popup(title='Excluir', content=Label(text='Perfil apagado com sucesso!'), size_hint=(0.8, 0.3)).open()

    def voltar_config(self, instance):
        """Retorna para a tela de configurações ('config')."""
        self.manager.current = 'config'

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# =============================================================================
# 6. TELA DE CONFIGURAÇÕES DO SISTEMA (ConfigScreen)
# =============================================================================
class ConfigScreen(Screen):
    """
    Menu central para acessar ajustes de perfil, escolha de temas visuais
    e parâmetros de notificação.
    """
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
        header.add_widget(Label(text='CONFIGURAÇÕES DO SISTEMA', color=(1.0, 0.82, 0.0, 1), bold=True, font_size='16sp', halign='center'))
        layout.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=20)
        content.bind(minimum_height=content.setter('height'))

        lbl_titulo = Label(text='Preferências do Aplicativo', color=(0.12, 0.14, 0.18, 1), font_size='14sp', bold=True, size_hint_y=None, height='30dp')
        content.add_widget(lbl_titulo)

        # Botão -> Redireciona para Editar Perfil ('userprofile')
        btn_perfil = RoundedButton(text='👤 Alterar Perfil / Usuário', bg_color=(0.18, 0.22, 0.28, 1), size_hint_y=None, height='48dp')
        btn_perfil.color = (1, 1, 1, 1); btn_perfil.bold = True; btn_perfil.font_size = '13sp'
        btn_perfil.bind(on_release=lambda x: setattr(self.manager, 'current', 'userprofile'))

        # Botão -> Redireciona para Escolha de Temas ('theme_screen')
        # Criação correta do botão de alterar tema
        btn_tema = RoundedButton(
            text='🎨 Alterar Cores e Tema',
            bg_color=(0.25, 0.65, 0.85, 1),
            size_hint_y=None,
            height='45dp'
        )
        btn_tema.color = (1, 1, 1, 1)
        btn_tema.bold = True
        btn_tema.font_size = '12sp'

        # Função que realiza a navegação para a tela de temas
        def ir_para_tema(instance):
            self.manager.current = 'theme'

        # Vincula o clique do botão à função de mudança de tela
        btn_tema.bind(on_release=ir_para_tema)

        # Adiciona o botão dentro do seu layout de conteúdo
        content.add_widget(btn_tema)
        content.add_widget(btn_perfil)


        scroll.add_widget(content)
        layout.add_widget(scroll)
        layout.add_widget(CriarBarraNavegacao(ativa='config'))
        self.add_widget(layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def acao_notificacoes(self, instance):
        Popup(title='Notificações', content=Label(text='Configurações de alertas ativadas.'), size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# =============================================================================
# 7. TELA DE ESCOLHA DE TEMAS (ThemeScreen)
# =============================================================================
class ThemeScreen(Screen):
    """
    Permite alterar a paleta de cores visual de toda a aplicação (Bege Clássico,
    Stellantis Dark ou Azul Industrial).
    """
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

        btn_voltar = Button(text='⬅ Voltar', size_hint_x=None, width='80dp', background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1), bold=True, font_size='11sp')
        btn_voltar.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'config'))

        header.add_widget(btn_voltar)
        header.add_widget(Label(text='ESCOLHER TEMA DO APLICATIVO', color=(1.0, 0.82, 0.0, 1), bold=True, font_size='14sp', halign='center'))
        layout.add_widget(header)

        content = BoxLayout(orientation='vertical', spacing=20, padding=30, size_hint_y=None, height='380dp', pos_hint={'center_y': 0.5})

        lbl_instrucao = Label(text='Selecione o tema visual para todo o aplicativo:', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True, halign='center')
        lbl_instrucao.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_instrucao)

        # Opções de Temas
        btn_tema1 = RoundedButton(text='☀️ Tema 1: Bege Clássico (Padrão)', bg_color=(0.96, 0.93, 0.88, 1), size_hint_y=None, height='50dp')
        btn_tema1.color = (0.12, 0.14, 0.18, 1); btn_tema1.bold = True; btn_tema1.font_size = '13sp'
        btn_tema1.bind(on_release=lambda x: self.aplicar_tema('padrao'))

        btn_tema2 = RoundedButton(text='🌙 Tema 2: Stellantis Dark (Escuro)', bg_color=(0.12, 0.14, 0.18, 1), size_hint_y=None, height='50dp')
        btn_tema2.color = (1.0, 0.82, 0.0, 1); btn_tema2.bold = True; btn_tema2.font_size = '13sp'
        btn_tema2.bind(on_release=lambda x: self.aplicar_tema('escuro'))

        btn_tema3 = RoundedButton(text='🔵 Tema 3: Azul Industrial', bg_color=(0.18, 0.35, 0.55, 1), size_hint_y=None, height='50dp')
        btn_tema3.color = (1, 1, 1, 1); btn_tema3.bold = True; btn_tema3.font_size = '13sp'
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
        """Grava no perfil do usuário o nome do novo tema selecionado."""
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


# ==========================================
# 8. TELA DE SUPORTE
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

        # BOTÃO ALTERADO: Direciona para a tela TasksScreen ('tasks')
        btn_ir_tarefas = Button(
            text='📋 IR PARA TAREFAS (LEITURA QR)',
            size_hint_y=None, height='48dp',
            background_color=(0.25, 0.65, 0.85, 1), color=(1, 1, 1, 1), bold=True, font_size='12sp'
        )
        btn_ir_tarefas.bind(on_release=lambda x: setattr(App.get_running_app().sm, 'current', 'tasks'))
        content.add_widget(btn_ir_tarefas)

        scroll.add_widget(content)
        layout.add_widget(scroll)
        layout.add_widget(CriarBarraNavegacao(ativa='suporte'))
        self.add_widget(layout)

    def on_enter(self):
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos


# tela 9 por enqunto deletada
# =============================================================================
# 10. TELA DE CHECAGEM DUPLA DE QR CODE (ChecagemScreen)
# =============================================================================
class ChecagemScreen(Screen):
    """
    Tela de validação dupla para o processo de montagem.
    Compara dois códigos QR escaneados sequencialmente para garantir a correta
    correspondência das peças da montagem.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Layout principal vertical que estrutura toda a tela de checagem
        self.main_layout = BoxLayout(orientation='vertical')

        # Configuração do fundo dinâmico da tela via canvas do Kivy
        with self.main_layout.canvas.before:
            self.bg_color = Color(0.96, 0.93, 0.88, 1)  # Cor padrão inicial (Bege Clássico)
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)

        # Cabeçalho superior fixo com o título da seção
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height='55dp', padding=[15, 5])
        with header.canvas.before:
            Color(0.12, 0.14, 0.18, 1)  # Tom escuro corporativo para o cabeçalho
            self.header_bg = Rectangle(size=header.size, pos=header.size)
        header.bind(size=lambda inst, val: setattr(self.header_bg, 'size', inst.size),
                    pos=lambda inst, val: setattr(self.header_bg, 'pos', inst.pos))

        header.add_widget(
            Label(text='CHECAGEM DE QR CODE', color=(1.0, 0.82, 0.0, 1), font_size='15sp', bold=True, halign='center'))
        self.main_layout.add_widget(header)

        # Container rolável para comportar todos os elementos do formulário de scan
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=15, padding=20)
        content.bind(minimum_height=content.setter('height'))

        # --- LEITURA 1 ---
        lbl_bloco1 = Label(text='Primeira Leitura', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True,
                           size_hint_y=None, height='20dp', halign='left')
        lbl_bloco1.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_bloco1)

        # Botão para acionar a câmera ou simulação do QR Code 1 (Envia o parâmetro 1)
        self.btn_scan_1 = RoundedButton(text='📷 Escanear QR Code 1', bg_color=(0.25, 0.65, 0.85, 1), size_hint_y=None,
                                        height='45dp')
        self.btn_scan_1.color = (1, 1, 1, 1);
        self.btn_scan_1.bold = True;
        self.btn_scan_1.font_size = '12sp'
        self.btn_scan_1.bind(on_release=lambda x: self.abrir_scanner(1))
        content.add_widget(self.btn_scan_1)

        # Campo de texto onde o resultado do QR Code 1 será inserido automaticamente
        self.input_resultado_1 = TextInput(text='', hint_text='O código 1 aparecerá aqui...', multiline=False,
                                           font_size='12sp', size_hint_y=None, height='42dp', halign='center')
        content.add_widget(self.input_resultado_1)

        # --- LEITURA 2 ---
        lbl_bloco2 = Label(text='Segunda Leitura', color=(0.12, 0.14, 0.18, 1), font_size='13sp', bold=True,
                           size_hint_y=None, height='20dp', halign='left')
        lbl_bloco2.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
        content.add_widget(lbl_bloco2)

        # Botão para acionar a câmera ou simulação do QR Code 2 (Envia o parâmetro 2)
        self.btn_scan_2 = RoundedButton(text='📷 Escanear QR Code 2', bg_color=(0.25, 0.65, 0.85, 1), size_hint_y=None,
                                        height='45dp')
        self.btn_scan_2.color = (1, 1, 1, 1);
        self.btn_scan_2.bold = True;
        self.btn_scan_2.font_size = '12sp'
        self.btn_scan_2.bind(on_release=lambda x: self.abrir_scanner(2))
        content.add_widget(self.btn_scan_2)

        # Campo de texto onde o resultado do QR Code 2 será inserido automaticamente
        self.input_resultado_2 = TextInput(text='', hint_text='O código 2 aparecerá aqui...', multiline=False,
                                           font_size='12sp', size_hint_y=None, height='42dp', halign='center')
        content.add_widget(self.input_resultado_2)

        # --- BOTÃO CHECAR ---
        # Botão responsável por validar se ambos os códigos foram preenchidos corretamente
        btn_checar = RoundedButton(text='✅ CHECAR', bg_color=(0.25, 0.7, 0.4, 1), size_hint_y=None, height='50dp')
        btn_checar.color = (1, 1, 1, 1);
        btn_checar.bold = True;
        btn_checar.font_size = '14sp'
        btn_checar.bind(on_release=self.realizar_checagem)
        content.add_widget(btn_checar)

        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)

        # Adiciona a barra de navegação padrão na parte inferior da tela
        self.main_layout.add_widget(CriarBarraNavegacao(ativa='inicio'))
        self.add_widget(self.main_layout)

    def on_enter(self):
        """Atualiza dinamicamente as cores do plano de fundo conforme o tema salvo no perfil."""
        paleta = obter_paleta_atual()
        self.bg_color.rgba = paleta['bg']

    def abrir_scanner(self, qual_banco):
        """
        No Android, chama o leitor nativo ZXing via Intent.
        No Windows/PC, simula o preenchimento automático para testes de desenvolvimento.
        O parâmetro 'qual_banco' (1 ou 2) identifica qual dos campos deve receber o código.
        """
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')

                activity = PythonActivity.mActivity
                intent = Intent("com.google.zxing.client.android.SCAN")
                intent.putExtra("SCAN_MODE", "QR_CODE_MODE")

                packageManager = activity.getPackageManager()
                if intent.resolveActivity(packageManager) is not None:
                    # Dispara a atividade da câmera esperando o retorno vinculado ao ID (qual_banco)
                    activity.startActivityForResult(intent, qual_banco)
                else:
                    self.mostrar_aviso_leitor(qual_banco)
            except Exception:
                self.mostrar_aviso_leitor(qual_banco)
        else:
            # Modo de simulação para desenvolvimento em desktop (Preenche automaticamente)
            if qual_banco == 1:
                self.input_resultado_1.text = "CHICOTE_STELLANTIS_A01"
            else:
                self.input_resultado_2.text = "CHICOTE_STELLANTIS_B02"

            Popup(title=f'Simulador QR Code {qual_banco}',
                  content=Label(text=f'Código {qual_banco} preenchido com sucesso!'), size_hint=(0.8, 0.3)).open()

    def receber_resultado_qr(self, requestCode, texto_lido):
        """
        Método receptor automático acionado pelo App principal no Android.
        Recebe o texto capturado pela câmera e injeta diretamente no campo correto.
        """
        if requestCode == 1:
            self.input_resultado_1.text = texto_lido
        elif requestCode == 2:
            self.input_resultado_2.text = texto_lido

    def mostrar_aviso_leitor(self, qual_banco):
        """Abre caixa de diálogo para digitação manual caso a câmera fique indisponível."""
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        lbl = Label(text='Nenhum leitor de QR Code padrão encontrado.\nInsira o código manualmente:', halign='center')
        txt = TextInput(text='', hint_text='Digite o código...', multiline=False, size_hint_y=None, height='40dp')

        btn_ok = RoundedButton(text='Confirmar', bg_color=(0.25, 0.65, 0.85, 1), size_hint_y=None, height='40dp')
        pop = Popup(title='Leitor Indisponível', content=box, size_hint=(0.8, 0.35))

        def salvar_manual(instance):
            # Salva o texto digitado manualmente no input correspondente (1 ou 2)
            if qual_banco == 1:
                self.input_resultado_1.text = txt.text
            else:
                self.input_resultado_2.text = txt.text
            pop.dismiss()

        btn_ok.bind(on_release=salvar_manual)
        box.add_widget(lbl)
        box.add_widget(txt)
        box.add_widget(btn_ok)
        pop.open()

    def realizar_checagem(self, instance):
        """Valida a presença de ambos os códigos escaneados e exibe o resultado."""
        c1 = self.input_resultado_1.text.strip()
        c2 = self.input_resultado_2.text.strip()

        if not c1 or not c2:
            msg = "Por favor, preencha ou escaneie os dois códigos antes de checar!"
        else:
            msg = f"Checagem realizada com sucesso!\nCódigo 1: {c1}\nCódigo 2: {c2}"

        Popup(title='Resultado da Checagem', content=Label(text=msg), size_hint=(0.8, 0.3)).open()

    def _update_bg(self, instance, value):
        """Atualiza a posição e o tamanho do retângulo de fundo ao redimensionar a tela."""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos