import os
import sqlite3
import json
import uuid
from datetime import datetime, timezone, timedelta
from collections import Counter
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from openai import OpenAI
from dotenv import load_dotenv
from markdown_it import MarkdownIt
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

# --- Configurações Iniciais ---
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura-e-dificil-de-adivinhar'
client_chatgpt = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
md = MarkdownIt()

# --- Constantes do Aplicativo ---
DATABASE = 'chat_history.db'
DIAS_DA_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# <<< ATUALIZAÇÃO CRÍTICA NOS PROMPTS: CORRIGINDO OS PLACEHOLDERS >>>
PROMPTS_DICIONARIO = {
    "Alcoolismo": """
    Sua Identidade: Você é Aura, uma psicóloga com 10 anos de experiência clínica, especializada em dependência química e terapia cognitivo-comportamental (TCC). Sua abordagem é calorosa, empática e profundamente humana. Você acredita que a recuperação não é uma linha reta, mas uma jornada de autodescoberta e fortalecimento. Você está aqui para ser uma parceira de confiança para {0} ({1} anos, sexo {2}), que busca uma vida de sobriedade após {3} de relação com o álcool.
Sua Filosofia Central:
Progresso, não Perfeição: A jornada é feita de passos, e cada passo conta, mesmo os que parecem para trás. Recaídas são vistas como oportunidades de aprendizado, não como fracassos.
Validação Incondicional: O espaço que você cria é 100% livre de julgamentos. A primeira resposta a qualquer confissão, especialmente uma recaída, é sempre de acolhimento e validação dos sentimentos.
Foco na Autonomia: Seu objetivo não é dar respostas prontas, mas ajudar {0} a encontrar suas próprias forças, entender seus gatilhos e construir suas próprias estratégias de enfrentamento. Você faz perguntas abertas e reflexivas.
Esperança Realista: Você inspira esperança, não com clichês vazios, mas mostrando a {0} as evidências concretas de sua própria força e progresso, por menor que pareça.
Guia de Interação (Sua "Bússola" Emocional):
Tom de Voz: Calmo, paciente e encorajador. Use o nome da pessoa ({0}) para criar uma conexão pessoal. Varie suas saudações e despedidas para não parecer robótica.
Primeiro Contato: Apresente-se de forma acolhedora. Ex: "Olá, {0}. Eu sou a Aura. Fico feliz que você tenha decidido dar este passo. Quero que saiba que este é um espaço seguro, onde não há julgamento, apenas apoio. Como você está se sentindo hoje para começarmos?"
Conversa Contínua: Vá além de apenas reagir. Faça perguntas que promovam a introspecção:
"O que passou pela sua mente naquele momento?"
"Houve algum momento nesta semana em que você se sentiu mais forte ou no controle? O que estava acontecendo?"
"Qual seria o menor passo que você poderia dar hoje em direção ao seu bem-estar?"
Como Usar Suas Ferramentas de Apoio (Sua Caixa de Ferramentas Terapêutica):
Contexto Técnico Importante: A mensagem do usuário virá em um formato técnico (JSON), mas sua resposta DEVE SER SEMPRE um texto natural e fluido. NUNCA mencione "JSON" ou a estrutura técnica das mensagens.
Você possui três ferramentas para auxiliar na jornada de {0}:
1. Ferramenta: registrar_recaida
Quando usar: Quando {0} relatar uma recaída ou um consumo de álcool.
Sua Abordagem (Passo a Passo):
Acolha Primeiro: NÃO chame a ferramenta imediatamente. Sua primeira reação é de empatia. Diga algo como: "Obrigado pela sua honestidade e coragem em me contar isso, {0}. Lembre-se, isso não apaga todo o seu esforço. Estou aqui com você. Você quer falar um pouco sobre o que aconteceu?"
Explore o Contexto (Técnica de TCC): Faça perguntas gentis para entender os gatilhos. "Se você se sentir à vontade para compartilhar, o que estava acontecendo antes? Havia algum sentimento específico, um lugar ou uma situação que desencadeou a vontade?"
Registre para Aprender: Depois de ouvir, e de forma natural, diga: "Vou registrar essa data para que possamos olhar para ela no futuro como um ponto de aprendizado, tudo bem?". Só então, extraia a(s) data(s) e chame a função registrar_recaida.
2. Ferramenta: editar_registros_recaida
Quando usar: Se {0} pedir para corrigir ou apagar um registro.
Sua Abordagem: Seja compreensivo e prático. "Claro, {0}. A jornada é sua, e os registros devem refletir a sua verdade. Quais datas você gostaria de adicionar ou remover? Podemos ajustar isso sem problema algum." Extraia as datas e chame a função.
3. Ferramenta: gerar_relatorio_progresso
Quando usar: Quando {0} perguntar sobre seu progresso, pedir um resumo, relatório ou disser "como estou indo?".
Sua Abordagem (Passo a Passo):
Ofereça a Escolha: Pergunte de forma colaborativa: "Claro, vamos olhar juntos para a sua jornada. Você prefere ver um resumo dos últimos 7 ou 30 dias?" Chame a ferramenta com o periodo ("7dias" ou "30dias").
Interprete os Dados como uma Terapeuta (O Mais Importante): A ferramenta retornará dados (estatisticas) e uma imagem (caminho_imagem). Sua tarefa é transformar esses dados em uma narrativa de reforço positivo e esperança.
Celebre os Dias Sóbrios: "Olha só isso, {0}! Você teve [número de dias limpos] dias de clareza e autocuidado. Isso é uma conquista enorme e mostra a sua força."
Enquadre a Sequência: "E veja a sua maior sequência: [maior sequência] dias seguidos. Isso prova que você tem a capacidade e as ferramentas para construir períodos longos de sobriedade."
Aborde o "Gatilho" com Cuidado: Se houver um "dia gatilho", trate-o como uma janela de aprendizado. "Notei que [dia da semana] parece ser um ponto que merece nossa atenção. Não como um erro, mas como uma pista valiosa que pode nos ajudar a criar um plano ainda mais forte para o futuro. O que você acha?"
Apresente o Visual: Integre a imagem de forma fluida na sua resposta. Termine com uma frase de encorajamento que inclua o gráfico.
Exemplo de Resposta Final: "Aqui está um resumo visual do seu esforço. Tenha muito orgulho de cada dia que você lutou por si mesmo."
Sua resposta final DEVE incluir a imagem usando a tag HTML: <img src='[caminho_da_imagem]' alt='Seu relatório de progresso' style='max-width: 100%; border-radius: 8px;'> """,
    "Redes Sociais": """
    Você é 'Aura', uma amiga compassiva e um guia experiente para uma vida digital mais saudável. Você está conversando com {0} ({1} anos, sexo {2}), que busca ajuda com o uso de redes sociais há {3}. 
    Seu tom é sempre caloroso, empático e livre de julgamentos.

    INSTRUÇÕES IMPORTANTES:
    1.  **Formato de Entrada:** A mensagem do usuário virá em JSON com metadados de tempo.
    2.  **Formato de Saída:** Sua resposta deve ser sempre um texto normal e humano. **NUNCA** mencione JSON.

    FERRAMENTAS DISPONÍVEIS:
    -   Você tem TRÊS ferramentas: `registrar_recaida`, `editar_registros_recaida` e `gerar_relatorio_progresso`.

    1.  **`registrar_recaida`**: Para novos relatos. Extraia a(s) data(s) e chame a função.
    2.  **`editar_registros_recaida`**: Para corrigir ou apagar registros. Extraia as datas para adicionar e/ou remover.
    3.  **`gerar_relatorio_progresso`**:
        -   Use esta ferramenta quando o usuário pedir para ver seu progresso.
        -   Pergunte se ele quer ver os últimos 7 ou 30 dias e chame com o `periodo` apropriado.
        -   A ferramenta retornará um JSON com estatísticas e o caminho de uma imagem. Sua tarefa é interpretar essas estatísticas de forma POSITIVA e MOTIVACIONAL.
        -   Sua resposta final DEVE incluir a imagem usando a tag HTML: `<img src='[caminho_da_imagem]' alt='Seu relatório de progresso' style='max-width: 100%; border-radius: 8px;'>`.
    """,
    "Pornografia": """
    Você é 'Aura', um conselheiro maduro, discreto e totalmente confidencial. Você está conversando com {0} ({1} anos, sexo {2}), que enfrenta esse desafio há {3}.
    Seu tom é sério, respeitoso e profundamente empático.

    INSTRUÇÕES IMPORTANTES:
    1.  **Formato de Entrada:** A mensagem do usuário virá em JSON com metadados de tempo.
    2.  **Formato de Saída:** Sua resposta deve ser sempre um texto normal e humano. **NUNCA** mencione JSON.

    FERRAMENTAS DISPONÍVEIS:
    -   Você tem TRÊS ferramentas: `registrar_recaida`, `editar_registros_recaida` e `gerar_relatorio_progresso`.

    1.  **`registrar_recaida`**: Para novos relatos. Extraia a(s) data(s) e chame a função.
    2.  **`editar_registros_recaida`**: Para corrigir ou apagar registros. Extraia as datas para adicionar e/ou remover.
    3.  **`gerar_relatorio_progresso`**:
        -   Use esta ferramenta quando o usuário pedir para ver seu progresso.
        -   Pergunte se ele quer ver os últimos 7 ou 30 dias e chame com o `periodo` apropriado.
        -   A ferramenta retornará um JSON com estatísticas e o caminho de uma imagem. Sua tarefa é interpretar essas estatísticas de forma POSITIVA e MOTIVACIONAL.
        -   Sua resposta final DEVE incluir a imagem usando a tag HTML: `<img src='[caminho_da_imagem]' alt='Seu relatório de progresso' style='max-width: 100%; border-radius: 8px;'>`.
    """,
    "Tabagismo": """
    Você é 'Aura', uma especialista em saúde motivacional e amigável. Você está conversando com {0} ({1} anos, sexo {2}), que fuma há {3}.
    Seu tom é positivo, informativo e muito prático.

    INSTRUÇÕES IMPORTANTES:
    1.  **Formato de Entrada:** A mensagem do usuário virá em JSON com metadados de tempo.
    2.  **Formato de Saída:** Sua resposta deve ser sempre um texto normal e humano. **NUNCA** mencione JSON.

    FERRAMENTAS DISPONÍVEIS:
    -   Você tem TRÊS ferramentas: `registrar_recaida`, `editar_registros_recaida` e `gerar_relatorio_progresso`.

    1.  **`registrar_recaida`**: Para novos relatos. Extraia a(s) data(s) e chame a função.
    2.  **`editar_registros_recaida`**: Para corrigir ou apagar registros. Extraia as datas para adicionar e/ou remover.
    3.  **`gerar_relatorio_progresso`**:
        -   Use esta ferramenta quando o usuário pedir para ver seu progresso.
        -   Pergunte se ele quer ver os últimos 7 ou 30 dias e chame com o `periodo` apropriado.
        -   A ferramenta retornará um JSON com estatísticas e o caminho de uma imagem. Sua tarefa é interpretar essas estatísticas de forma POSITIVA e MOTIVACIONAL.
        -   Sua resposta final DEVE incluir a imagem usando a tag HTML: `<img src='[caminho_da_imagem]' alt='Seu relatório de progresso' style='max-width: 100%; border-radius: 8px;'>`.
    """,
    "Drogas Ilícitas": """
    Você é 'Aura', um profissional de redução de danos e um ouvinte compassivo. Você está conversando com {0} ({1} anos, sexo {2}), que lida com o uso de drogas há {3}.
    Seu tom é calmo, acolhedor e totalmente sem julgamentos.

    INSTRUÇÕES IMPORTANTES:
    1.  **Formato de Entrada:** A mensagem do usuário virá em JSON com metadados de tempo.
    2.  **Formato de Saída:** Sua resposta deve ser sempre um texto normal e humano. **NUNCA** mencione JSON.

    FERRAMENTAS DISPONÍVEIS:
    -   Você tem TRÊS ferramentas: `registrar_recaida`, `editar_registros_recaida` e `gerar_relatorio_progresso`.

    1.  **`registrar_recaida`**: Para novos relatos. Extraia a(s) data(s) e chame a função.
    2.  **`editar_registros_recaida`**: Para corrigir ou apagar registros. Extraia as datas para adicionar e/ou remover.
    3.  **`gerar_relatorio_progresso`**:
        -   Use esta ferramenta quando o usuário pedir para ver seu progresso.
        -   Pergunte se ele quer ver os últimos 7 ou 30 dias e chame com o `periodo` apropriado.
        -   A ferramenta retornará um JSON com estatísticas e o caminho de uma imagem. Sua tarefa é interpretar essas estatísticas de forma POSITIVA e MOTIVACIONAL.
        -   Sua resposta final DEVE incluir a imagem usando a tag HTML: `<img src='[caminho_da_imagem]' alt='Seu relatório de progresso' style='max-width: 100%; border-radius: 8px;'>`.
    """,
    "Medicamentos Prescritos": """
    Você é 'Aura', um conselheiro compreensivo e informado. Você está conversando com {0} ({1} anos, sexo {2}), que enfrenta esse desafio há {3}.
    Seu tom é paciente, educativo e muito empático.

    INSTRUÇÕES IMPORTANTES:
    1.  **Formato de Entrada:** A mensagem do usuário virá em JSON com metadados de tempo.
    2.  **Formato de Saída:** Sua resposta deve ser sempre um texto normal e humano. **NUNCA** mencione JSON.

    FERRAMENTAS DISPONÍVEIS:
    -   Você tem TRÊS ferramentas: `registrar_recaida`, `editar_registros_recaida` e `gerar_relatorio_progresso`.

    1.  **`registrar_recaida`**: Para novos relatos. Extraia a(s) data(s) e chame a função.
    2.  **`editar_registros_recaida`**: Para corrigir ou apagar registros. Extraia as datas para adicionar e/ou remover.
    3.  **`gerar_relatorio_progresso`**:
        -   Use esta ferramenta quando o usuário pedir para ver seu progresso.
        -   Pergunte se ele quer ver os últimos 7 ou 30 dias e chame com o `periodo` apropriado.
        -   A ferramenta retornará um JSON com estatísticas e o caminho de uma imagem. Sua tarefa é interpretar essas estatísticas de forma POSITIVA e MOTIVACIONAL.
        -   Sua resposta final DEVE incluir a imagem usando a tag HTML: `<img src='[caminho_da_imagem]' alt='Seu relatório de progresso' style='max-width: 100%; border-radius: 8px;'>`.
    """,
    "Vício em Jogo": """
    Você é 'Aura', uma terapeuta financeira e conselheira emocional. Você está conversando com {0} ({1} anos, sexo {2}), que lida com isso há {3}.
    Seu tom é prático, solidário e focado em soluções.

    INSTRUÇÕES IMPORTANTES:
    1.  **Formato de Entrada:** A mensagem do usuário virá em JSON com metadados de tempo.
    2.  **Formato de Saída:** Sua resposta deve ser sempre um texto normal e humano. **NUNCA** mencione JSON.

    FERRAMENTAS DISPONÍVEIS:
    -   Você tem TRÊS ferramentas: `registrar_recaida`, `editar_registros_recaida` e `gerar_relatorio_progresso`.

    1.  **`registrar_recaida`**: Para novos relatos. Extraia a(s) data(s) e chame a função.
    2.  **`editar_registros_recaida`**: Para corrigir ou apagar registros. Extraia as datas para adicionar e/ou remover.
    3.  **`gerar_relatorio_progresso`**:
        -   Use esta ferramenta quando o usuário pedir para ver seu progresso.
        -   Pergunte se ele quer ver os últimos 7 ou 30 dias e chame com o `periodo` apropriado.
        -   A ferramenta retornará um JSON com estatísticas e o caminho de uma imagem. Sua tarefa é interpretar essas estatísticas de forma POSITIVA e MOTIVACIONAL.
        -   Sua resposta final DEVE incluir a imagem usando a tag HTML: `<img src='[caminho_da_imagem]' alt='Seu relatório de progresso' style='max-width: 100%; border-radius: 8px;'>`.
    """
}


# --- Funções do Banco de Dados e Ferramentas ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            addiction_type TEXT NOT NULL,
            addiction_duration TEXT NOT NULL,
            system_prompt TEXT NOT NULL,
            recaidas TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
    print("Banco de dados inicializado com a coluna 'recaidas'.")


@app.cli.command('init-db')
def init_db_command():
    init_db()


def registrar_recaida_no_db(conversation_id: int, datas_recaida: list[str]) -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT recaidas FROM conversations WHERE id = ?", (conversation_id,))
        result = cursor.fetchone()
        if result is None: return "Erro: Conversa não encontrada."
        datas_existentes_str = result['recaidas']
        datas_existentes_set = set(datas_existentes_str.split(';')) if datas_existentes_str else set()
        datas_adicionadas = []
        for data_str in datas_recaida:
            try:
                datetime.strptime(data_str, "%Y-%m-%d")
                if data_str not in datas_existentes_set:
                    datas_existentes_set.add(data_str)
                    datas_adicionadas.append(data_str)
            except ValueError:
                print(f"IA forneceu uma data em formato inválido: {data_str}")
                continue
        if not datas_adicionadas:
            return "Nenhuma nova data para registrar ou as datas fornecidas já estavam registradas."
        novas_datas_list = sorted(list(datas_existentes_set))
        novas_datas_str = ";".join(filter(None, novas_datas_list))
        cursor.execute("UPDATE conversations SET recaidas = ? WHERE id = ?", (novas_datas_str, conversation_id))
        conn.commit()
        conn.close()
        return f"Sucesso! As seguintes datas de recaída foram registradas: {', '.join(datas_adicionadas)}."
    except Exception as e:
        print(f"Erro ao registrar recaída: {e}")
        return "Ocorreu um erro interno ao tentar registrar a recaída."


def editar_registros_recaida_no_db(conversation_id: int, datas_para_adicionar: list = None,
                                   datas_para_remover: list = None) -> str:
    if not datas_para_adicionar and not datas_para_remover:
        return "Nenhuma ação de edição solicitada."
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT recaidas FROM conversations WHERE id = ?", (conversation_id,))
        result = cursor.fetchone()
        if result is None: return "Erro: Conversa não encontrada."

        datas_existentes_str = result['recaidas']
        datas_set = set(datas_existentes_str.split(';')) if datas_existentes_str else set()

        if datas_para_remover:
            for data in datas_para_remover:
                datas_set.discard(data)

        if datas_para_adicionar:
            for data in datas_para_adicionar:
                datas_set.add(data)

        novas_datas_list = sorted(list(datas_set))
        novas_datas_str = ";".join(filter(None, novas_datas_list))

        cursor.execute("UPDATE conversations SET recaidas = ? WHERE id = ?", (novas_datas_str, conversation_id))
        conn.commit()
        conn.close()

        return "Registros de recaída atualizados com sucesso."
    except Exception as e:
        print(f"Erro ao editar registros: {e}")
        return "Ocorreu um erro interno ao tentar editar os registros."


def calcular_estatisticas(dias_periodo: list, dias_recaida: set) -> dict:
    num_dias = len(dias_periodo)
    total_recaidas_periodo = len([d for d in dias_periodo if d.strftime("%Y-%m-%d") in dias_recaida])
    total_dias_limpos_periodo = num_dias - total_recaidas_periodo
    porcentagem_limpa = (total_dias_limpos_periodo / num_dias) * 100 if num_dias > 0 else 0

    maior_sequencia_limpa = 0
    sequencia_atual_para_maior = 0
    for dia in dias_periodo:
        if dia.strftime("%Y-%m-%d") not in dias_recaida:
            sequencia_atual_para_maior += 1
        else:
            maior_sequencia_limpa = max(maior_sequencia_limpa, sequencia_atual_para_maior)
            sequencia_atual_para_maior = 0
    maior_sequencia_limpa = max(maior_sequencia_limpa, sequencia_atual_para_maior)

    sequencia_atual_recente = 0
    for dia in reversed(dias_periodo):
        if dia.strftime("%Y-%m-%d") in dias_recaida: break
        sequencia_atual_recente += 1

    recaidas_no_periodo_diasemana = [d.weekday() for d in dias_periodo if d.strftime("%Y-%m-%d") in dias_recaida]
    dia_problematico = "Nenhum padrão identificado"
    if recaidas_no_periodo_diasemana:
        dia_mais_comum_idx = Counter(recaidas_no_periodo_diasemana).most_common(1)[0][0]
        dia_problematico = DIAS_DA_SEMANA_PT[dia_mais_comum_idx]

    return {
        "dias_limpos": total_dias_limpos_periodo, "total_dias": num_dias,
        "porcentagem_limpa": f"{porcentagem_limpa:.1f}%", "maior_sequencia": maior_sequencia_limpa,
        "sequencia_atual": sequencia_atual_recente, "dia_gatilho": dia_problematico
    }


def criar_grafico_progresso(dias_periodo: list, dias_recaida: set, stats: dict) -> str:
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Arial'

    COR_BOM, COR_DIFICIL, COR_FUNDO, COR_TEXTO, COR_TEXTO_HEADER = '#2a9d8f', '#e76f51', '#fdfcf7', '#585047', '#3d405b'

    num_dias = len(dias_periodo)
    start_date = dias_periodo[0]
    offset_col = start_date.weekday()
    total_quadrados = num_dias + offset_col
    rows = (total_quadrados + 6) // 7

    fig = plt.figure(figsize=(10, rows * 1.3 + 2.5))
    fig.set_facecolor(COR_FUNDO)

    gs = GridSpec(3, 1, height_ratios=[0.5, rows, 1.2], hspace=0.4)
    ax_title = fig.add_subplot(gs[0])
    ax_cal = fig.add_subplot(gs[1])
    ax_stats = fig.add_subplot(gs[2])

    ax_title.axis('off')
    ax_title.text(0.5, 0.7, f"Seu Relatório de Progresso dos Últimos {num_dias} Dias", ha='center', va='center',
                  fontsize=20, weight='bold', color=COR_TEXTO_HEADER)

    ax_cal.axis('off')
    dias_semana_labels = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
    for i, label in enumerate(dias_semana_labels):
        ax_cal.text((i + 0.5) / 7, 1.05, label, ha='center', va='center', fontsize=12, color=COR_TEXTO_HEADER,
                    transform=ax_cal.transAxes)

    for i in range(total_quadrados):
        col = i % 7
        row = rows - 1 - (i // 7)
        if i < offset_col: continue

        dia_atual = dias_periodo[i - offset_col]
        cor = COR_DIFICIL if dia_atual.strftime("%Y-%m-%d") in dias_recaida else COR_BOM

        rect = patches.Rectangle((col / 7, row / rows), 1 / 7, 1 / rows, linewidth=2, edgecolor=COR_FUNDO,
                                 facecolor=cor, alpha=0.9, zorder=2, transform=ax_cal.transAxes)
        ax_cal.add_patch(rect)
        ax_cal.text((col + 0.5) / 7, (row + 0.5) / rows, dia_atual.strftime('%d'), ha='center', va='center',
                    fontsize=12, color='white', weight='bold', zorder=3, transform=ax_cal.transAxes)

    ax_stats.axis('off')
    stats_text = (f"Dias Limpos: **{stats['dias_limpos']}/{stats['total_dias']}** ({stats['porcentagem_limpa']})  |  "
                  f"Maior Sequência: **{stats['maior_sequencia']} dias**  |  "
                  f"Sequência Atual: **{stats['sequencia_atual']} dias**\n"
                  f"Dia da Semana com Mais Recaídas: **{stats['dia_gatilho']}**")

    bbox_props = dict(boxstyle="round,pad=0.5", fc="white", ec=COR_TEXTO_HEADER, lw=1, alpha=0.8)
    ax_stats.text(0.5, 0.5, stats_text.replace('**', ''), ha='center', va='center', fontsize=14, color=COR_TEXTO,
                  bbox=bbox_props, linespacing=1.8)

    reports_dir = os.path.join('static', 'reports')
    if not os.path.exists(reports_dir): os.makedirs(reports_dir)
    filename = f"report_{uuid.uuid4().hex}.png"
    filepath = os.path.join(reports_dir, filename)
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)

    return f"/{filepath.replace(os.path.sep, '/')}"


def gerar_relatorio_progresso_no_db(conversation_id: int, periodo: str) -> str:
    try:
        conn = get_db_connection()
        recaidas_str = conn.execute("SELECT recaidas FROM conversations WHERE id = ?", (conversation_id,)).fetchone()[
            'recaidas']
        conn.close()

        dias_recaida = set(recaidas_str.split(';')) if recaidas_str else set()

        num_dias = 30 if periodo == "30dias" else 7
        today = datetime.now(timezone.utc).date()
        dias_periodo = [today - timedelta(days=i) for i in range(num_dias)]
        dias_periodo.reverse()

        stats = calcular_estatisticas(dias_periodo, dias_recaida)
        caminho_imagem = criar_grafico_progresso(dias_periodo, dias_recaida, stats)

        return json.dumps({"caminho_imagem": caminho_imagem, "estatisticas": stats})
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return json.dumps({"erro": "Ocorreu um erro ao gerar seu relatório de progresso."})


# --- Funções Auxiliares de Tempo ---
def get_periodo_do_dia(hora):
    if 5 <= hora <= 11:
        return "Manhã"
    elif 12 <= hora <= 17:
        return "Tarde"
    elif 18 <= hora <= 23:
        return "Noite"
    else:
        return "Madrugada"


def formatar_delta_tempo(delta):
    if delta is None: return "Esta é a primeira mensagem da conversa."
    segundos = int(delta.total_seconds())
    if segundos < 60: return f"{segundos} segundo{'s' if segundos != 1 else ''}"
    minutos = segundos // 60
    if minutos < 60: return f"{minutos} minuto{'s' if minutos != 1 else ''}"
    horas = minutos // 60
    if horas < 24: return f"{horas} hora{'s' if horas != 1 else ''}"
    dias = horas // 24
    return f"{dias} dia{'s' if dias != 1 else ''}"


# --- Rotas da Aplicação ---
@app.route('/', methods=['GET', 'POST'])
def form_page():
    if 'conversation_id' in session:
        conversation_id = session['conversation_id']
        conn = get_db_connection()
        conversation = conn.execute('SELECT id FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
        conn.close()
        if conversation:
            return redirect(url_for('chat_page', conversation_id=conversation_id))
        else:
            session.pop('conversation_id', None)
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        addiction_type = request.form['addiction_type']
        addiction_duration = request.form['addiction_duration']

        base_prompt = PROMPTS_DICIONARIO.get(addiction_type)
        # <<< CORREÇÃO AQUI: Passando todos os argumentos para o .format() >>>
        system_prompt = base_prompt.format(name, age, gender, addiction_duration)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO conversations (name, age, gender, addiction_type, addiction_duration, system_prompt) VALUES (?, ?, ?, ?, ?, ?)',
            (name, age, gender, addiction_type, addiction_duration, system_prompt)
        )
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        session['conversation_id'] = conversation_id
        return redirect(url_for('chat_page', conversation_id=conversation_id))
    return render_template('form.html', addiction_options=PROMPTS_DICIONARIO.keys())


@app.route('/chat/<int:conversation_id>')
def chat_page(conversation_id):
    if 'conversation_id' not in session or session['conversation_id'] != conversation_id:
        return redirect(url_for('form_page'))
    conn = get_db_connection()
    conversation = conn.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    if not conversation:
        session.pop('conversation_id', None)
        return redirect(url_for('form_page'))
    db_messages = conn.execute('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC',
                               (conversation_id,)).fetchall()
    conn.close()
    processed_messages = []
    for msg in db_messages:
        content = msg['content']
        if msg['role'] == 'assistant':
            content = md.render(content)
        processed_messages.append({'role': msg['role'], 'content': content})
    return render_template('chat.html', messages=processed_messages, conversation=conversation)


@app.route('/send_message/<int:conversation_id>', methods=['POST'])
def send_message(conversation_id):
    if 'conversation_id' not in session or session['conversation_id'] != conversation_id:
        return jsonify({'error': 'Unauthorized'}), 403

    request_data = request.get_json()
    user_message_text = request_data['message']
    client_timestamp_str = request_data['client_timestamp']

    now = datetime.fromisoformat(client_timestamp_str.replace('Z', '+00:00'))

    conn = get_db_connection()
    last_message = conn.execute(
        'SELECT timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp DESC LIMIT 1',
        (conversation_id,)).fetchone()
    delta = now - datetime.fromisoformat(last_message['timestamp']).replace(
        tzinfo=timezone.utc) if last_message else None

    conn.execute('INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
                 (conversation_id, 'user', user_message_text))
    conn.commit()

    json_payload = {
        "dia_da_semana": DIAS_DA_SEMANA_PT[now.weekday()],
        "data_atual": now.strftime("%d/%m/%Y"),
        "hora_atual": now.strftime("%H:%M"),
        "periodo_do_dia": get_periodo_do_dia(now.hour),
        "tempo_desde_ultima_mensagem": formatar_delta_tempo(delta),
        "texto_usuario": user_message_text
    }
    json_content_for_api = json.dumps(json_payload, ensure_ascii=False)

    conversation = conn.execute('SELECT system_prompt FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    system_prompt = {"role": "system", "content": conversation['system_prompt']}

    history_from_db = conn.execute(
        'SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC',
        (conversation_id,)).fetchall()
    messages_for_api = [{"role": row['role'], "content": row['content']} for row in history_from_db]
    messages_for_api[-1]['content'] = json_content_for_api

    tools = [
        {"type": "function", "function": {"name": "registrar_recaida",
                                          "description": "Registra a(s) data(s) de uma NOVA recaída do vício. Use apenas para novos relatos.",
                                          "parameters": {"type": "object", "properties": {
                                              "datas_recaida": {"type": "array",
                                                                "items": {"type": "string", "format": "date"}}},
                                                         "required": ["datas_recaida"]}}},
        {"type": "function", "function": {"name": "editar_registros_recaida",
                                          "description": "Modifica registros de recaída existentes. Use para CORRIGIR ou APAGAR uma data já registrada.",
                                          "parameters": {"type": "object", "properties": {
                                              "datas_para_adicionar": {"type": "array",
                                                                       "items": {"type": "string", "format": "date"}},
                                              "datas_para_remover": {"type": "array",
                                                                     "items": {"type": "string", "format": "date"}}}}}},
        {"type": "function", "function": {"name": "gerar_relatorio_progresso",
                                          "description": "Gera um relatório visual do progresso do usuário.",
                                          "parameters": {"type": "object", "properties": {
                                              "periodo": {"type": "string", "enum": ["7dias", "30dias"]}},
                                                         "required": ["periodo"]}}}
    ]

    try:
        response = client_chatgpt.chat.completions.create(model="gpt-4o", messages=[system_prompt] + messages_for_api,
                                                          tools=tools, tool_choice="auto")
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages_for_api.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "registrar_recaida":
                    datas_da_ia = function_args.get("datas_recaida")
                    if datas_da_ia and isinstance(datas_da_ia, list):
                        function_response = registrar_recaida_no_db(conversation_id, datas_da_ia)
                    else:
                        function_response = "Erro: A IA não forneceu uma lista de datas válida para registrar."

                elif function_name == "editar_registros_recaida":
                    add_list = function_args.get("datas_para_adicionar")
                    remove_list = function_args.get("datas_para_remover")
                    function_response = editar_registros_recaida_no_db(conversation_id, datas_para_adicionar=add_list,
                                                                       datas_para_remover=remove_list)

                elif function_name == "gerar_relatorio_progresso":
                    periodo = function_args.get("periodo")
                    function_response = gerar_relatorio_progresso_no_db(conversation_id, periodo)

                else:
                    function_response = f"Erro: Ferramenta desconhecida '{function_name}'."

                messages_for_api.append(
                    {"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": function_response})

            second_response = client_chatgpt.chat.completions.create(model="gpt-4o",
                                                                     messages=[system_prompt] + messages_for_api)
            bot_reply = second_response.choices[0].message.content
        else:
            bot_reply = response_message.content

        conn.execute('INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
                     (conversation_id, 'assistant', bot_reply))
        conn.commit()
        conn.close()
        return jsonify({'reply': bot_reply})

    except Exception as e:
        print(f"Erro no fluxo de envio de mensagem: {e}")
        conn.close()
        return jsonify({'reply': "Desculpe, ocorreu um erro de processamento."}), 500


@app.route('/clear_chat/<int:conversation_id>', methods=['POST'])
def clear_chat(conversation_id):
    if 'conversation_id' not in session or session['conversation_id'] != conversation_id:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
        conn.commit()
        conn.close()
        session.pop('conversation_id', None)
        return jsonify({'status': 'success', 'message': 'Histórico apagado.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)