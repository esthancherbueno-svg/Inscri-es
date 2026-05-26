from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

app = Flask(__name__)

# ==============================
# CONFIGURAÇÕES
# ==============================

WEBHOOK_URL = "https://discord.com/api/webhooks/1208862663223017654/mFKELpWZMC_trZIW1ppZVmEUMrvi3EsPt3Z_HA6oEg2SYitBaAryZSv1wPFdaeNAc6R0"

# ==============================
# BANCO DE DADOS
# ==============================

conn = sqlite3.connect('equipes.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS equipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipe TEXT,
    capitao TEXT,
    discord TEXT,
    jogador1 TEXT,
    jogador2 TEXT,
    jogador3 TEXT,
    data TEXT
)
''')
conn.commit()

# ==============================
# HTML DA PÁGINA
# ==============================

HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title> Inscrições </title>
<style>
body {
    margin: 0;
    font-family: Arial;
    background: linear-gradient(135deg, #0a0a0a, #1a0033);
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
}

.container {
    width: 90%;
    max-width: 700px;
    background: rgba(255,255,255,0.05);
    padding: 30px;
    border-radius: 20px;
    box-shadow: 0 0 25px rgba(0,0,0,0.5);
}

h1 {
    text-align: center;
    color: #c084fc;
}

p {
    text-align: center;
    color: #cbd5e1;
}

label {
    display: block;
    margin-top: 15px;
    margin-bottom: 5px;
}

input {
    width: 100%;
    padding: 12px;
    border-radius: 10px;
    border: none;
    background: rgba(255,255,255,0.08);
    color: white;
}

button {
    width: 100%;
    padding: 15px;
    margin-top: 25px;
    border: none;
    border-radius: 12px;
    background: linear-gradient(90deg, #9333ea, #ec4899);
    color: white;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    opacity: 0.9;
}

.section {
    margin-top: 30px;
}

.section-title {
    color: #c084fc;
    font-size: 20px;
    margin-bottom: 10px;
}

.footer {
    text-align: center;
    margin-top: 20px;
    color: #94a3b8;
}
</style>
</head>
<body>

<form class="container" method="POST">
    <h1> Inscrições </h1>
    <p>Formulário oficial do torneio</p>

    <div class="section">
        <div class="section-title">Informações da Equipe</div>

        <label>Nome da Equipe</label>
        <input type="text" name="equipe" required>

        <label>Capitão</label>
        <input type="text" name="capitao" required>

        <label>Discord do Capitão</label>
        <input type="text" name="discord" required>
    </div>

    <div class="section">
        <div class="section-title">Integrantes</div>

        <label>Jogador 1 + id do discord</label>
        <input type="text" name="jogador1" required>

        <label>Jogador 2 + id do discord</label>
        <input type="text" name="jogador2" required>

        <label>Jogador 3 + id do discord</label>
        <input type="text" name="jogador3" required>
    </div>

    <button type="submit">Enviar Inscrição</button>

    <div class="footer">
        Boa sorte no campeonato 
    </div>
</form>

</body>
</html>
'''

# ==============================
# FUNÇÃO WEBHOOK DISCORD
# ==============================

def enviar_webhook(equipe, capitao, discord, j1, j2, j3):
    if not requests:
        return

    embed = {
        "title": "🏐 Nova Equipe Inscrita!",
        "color": 10181046,
        "fields": [
            {
                "name": "🏷️ Equipe",
                "value": equipe,
                "inline": False
            },
            {
                "name": "👑 Capitão",
                "value": f"{capitao} (Discord: {discord})",
                "inline": False
            },
            {
                "name": "👥 Jogadores",
                "value": f"1. {j1}\n2. {j2}\n3. {j3}",
                "inline": False
            }
        ]
    }

 try:
     response = requests.post(
          WEBHOOK_URL,
          json={"embeds": [embed]}
     )

      print("STATUS:", response.status_code)
      print("RESPOSTA:", response.text)
 except Exception as e:
      print(f"Erro ao enviar para o Discord: {e}")

# ==============================
# ROTAS
# ==============================

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        equipe = request.form['equipe']
        capitao = request.form['capitao']
        discord = request.form['discord']
        jogador1 = request.form['jogador1']
        jogador2 = request.form['jogador2']
        jogador3 = request.form['jogador3']

        data = datetime.now().strftime('%d/%m/%Y %H:%M')

        cursor.execute('''
        INSERT INTO equipes
        (equipe, capitao, discord, jogador1, jogador2, jogador3, data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (equipe, capitao, discord, jogador1, jogador2, jogador3, data))

        conn.commit()

        # Aqui estava o erro! Agora enviando todos os 6 dados certinho:
        enviar_webhook(equipe, capitao, discord, jogador1, jogador2, jogador3)

        return redirect('/')

    return render_template_string(HTML)

# ==============================
# PAINEL ADMIN
# ==============================

@app.route('/admin')
def admin():
    cursor.execute('SELECT * FROM equipes ORDER BY id DESC')
    equipes = cursor.fetchall()

    html = """
    <h1>Painel Admin - Equipes</h1>
    <table border='1' cellpadding='10'>
        <tr>
            <th>ID</th>
            <th>Equipe</th>
            <th>Capitão</th>
            <th>Discord</th>
            <th>Jogadores</th>
            <th>Data</th>
        </tr>
    """

    for eq in equipes:
        html += f"""
        <tr>
            <td>{eq[0]}</td>
            <td>{eq[1]}</td>
            <td>{eq[2]}</td>
            <td>{eq[3]}</td>
            <td>{eq[4]}, {eq[5]}, {eq[6]}</td>
            <td>{eq[7]}</td>
        </tr>
        """

    html += "</table>"
    return html

# ==============================
# INICIAR SERVIDOR
# ==============================

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
