from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os, json

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Diretórios e arquivos
DATA_DIR = 'data'
IMG_DIR = 'static/imagens'
OVERLAY_FILE = os.path.join(DATA_DIR, 'overlay.json')

# Cria diretórios
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# Utilitários de JSON
def load_json(nome):
    path = os.path.join(DATA_DIR, nome + '.json')
    if not os.path.exists(path):
        if nome in ['avisos', 'pacientes']:
            inicial = []        
        else:
            inicial = {}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(inicial, f, ensure_ascii=False, indent=2)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(nome, dados):
    path = os.path.join(DATA_DIR, nome + '.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# Overlay como fila de chamadas

def load_overlay_queue():
    if not os.path.exists(OVERLAY_FILE):
        with open(OVERLAY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    with open(OVERLAY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_overlay_queue(queue):
    with open(OVERLAY_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

# Rotas principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Adicionar paciente
        if 'salvar_paciente' in request.form:
            nome = request.form.get('novo_paciente', '').strip()
            if nome:
                lst = load_json('pacientes')
                lst.append({'nome': nome})  # sem sala ainda
                save_json('pacientes', lst)
                flash(f"Paciente '{nome}' adicionado com sucesso.")
            else:
                flash("Informe o nome do paciente.")

        # Chamar próximo paciente (admin, sem sala)
        if 'chamar_proximo' in request.form:
            lst = load_json('pacientes')
            if lst:
                prox = lst.pop(0)
                save_json('pacientes', lst)
                queue = load_overlay_queue()
                queue.append({'proximo': prox['nome'], 'sala': ''})
                save_overlay_queue(queue)
                flash(f"Próximo paciente '{prox['nome']}' chamado!")
            else:
                flash("Nenhum paciente na fila.")

        # Salvar avisos
        if 'salvar_avisos' in request.form:
            avisos = [a.strip() for a in request.form.get('avisos', '').split('\n') if a.strip()]
            save_json('avisos', avisos)
            flash("Avisos atualizados com sucesso.")

        # Upload de imagem
        if 'salvar_imagem' in request.form and 'imagem' in request.files:
            f = request.files['imagem']
            if f and f.filename:
                caminho = os.path.join(IMG_DIR, f.filename)
                f.save(caminho)
                flash(f"Imagem '{f.filename}' enviada com sucesso.")

        return redirect(url_for('admin'))

    return render_template('admin.html',
        pacientes=load_json('pacientes'),
        avisos=load_json('avisos'),
        imagens=sorted(os.listdir(IMG_DIR)),
    )

@app.route('/medico')
def medico_panel():
    return render_template('medico.html')

@app.route('/medico/chamar', methods=['POST'])
def medico_chamar():
    sala_medico = request.form.get('sala', '').strip()
    if not sala_medico:
        return jsonify({'status': 'error', 'msg': 'Informe a sala do médico'})

    lst = load_json('pacientes')
    if lst:
        prox = lst.pop(0)
        save_json('pacientes', lst)
        queue = load_overlay_queue()
        queue.append({'proximo': prox['nome'], 'sala': sala_medico})
        save_overlay_queue(queue)
        return jsonify({'status': 'ok', 'proximo': prox['nome'], 'sala': sala_medico})
    return jsonify({'status': 'empty'})

@app.route('/api/overlay')
def api_overlay():
    queue = load_overlay_queue()
    if queue:
        ov = queue.pop(0)
        save_overlay_queue(queue)
        return jsonify(ov)
    else:
        return jsonify({'proximo': '', 'sala': ''})

@app.route('/api/pacientes')
def api_pacientes():
    return jsonify(load_json('pacientes'))

@app.route('/api/avisos')
def api_avisos():
    return jsonify(load_json('avisos'))

@app.route('/api/imagens')
def api_imagens():
    return jsonify([url_for('static', filename='imagens/' + i) for i in sorted(os.listdir(IMG_DIR))])

@app.route('/delete/imagens/<nome>')
def delete_imagem(nome):
    path = os.path.join(IMG_DIR, nome)
    if os.path.exists(path):
        os.remove(path)
        flash(f"Imagem '{nome}' removida.")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)