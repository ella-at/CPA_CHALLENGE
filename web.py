from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
import cx_Oracle  
import requests
from datetime import datetime


app = Flask(__name__)
app.secret_key = '6acad0a12d21148a992875e2cf935d0a06c322eea013daf9' 


# Dados simulados (substitua por consulta ao banco de dados, quando ele voltar a funcionar !!!! -_- )
estoque = []
despesas = []
lucro_total = 0
despesas_totais = 0

# Dados simulados (substitua por consulta ao banco de dados, quando ele voltar a funcionar !!!! -_- )
estoque = [
    {'descricao': 'Sementes de Milho', 'tipo': 'semente', 'quantidade': 200, 'data_cadastro': '2024-09-01', 'data_expiracao': '2025-01-01', 'valor_unitario': 25, 'valor_total': 5000, 'lucro_estimado': 10000},
    {'descricao': 'Fertilizante', 'tipo': 'fertilizante', 'quantidade': 50, 'data_cadastro': '2024-08-15', 'data_expiracao': '2024-12-15', 'valor_unitario': 30, 'valor_total': 1500, 'lucro_estimado': 3000},
    # Outros itens...
]


# Dados simulados (substitua por consulta ao banco de dados, quando ele voltar a funcionar !!!! -_- )
equipamentos = [
    {
        'id': 1,
        'nome': 'Trator John Deere',
        'tipo': 'trator',
        'funcoes': ['preparacao_solo', 'cultivo'],
        'status': 'livre',
        'funcionario': None,
        'area_plantio': None,
        'ultima_manutencao': '2024-01-01',
        'proxima_manutencao': '2024-07-01'
    },
    {
        'id': 2,
        'nome': 'Pulverizador',
        'tipo': 'pulverizador',
        'funcoes': ['aplicacao_pesticida', 'limpeza'],
        'status': 'em atividade',
        'funcionario': 'José Silva',
        'area_plantio': 'Área A',
        'ultima_manutencao': '2024-03-01',
        'proxima_manutencao': '2024-09-01'
    }
]


# Dados simulados (substitua por consulta ao banco de dados, quando ele voltar a funcionar !!!! -_- )
funcionarios = [
    {
        'id': 1,
        'nome_completo': 'José da Silva',
        'aniversario': '1990-05-12',
        'cargo': 'Operador de Trator',
        'salario': 3000.00,
        'equipamentos': ['trator', 'arado'],
        'data_admissao': '2020-06-01',
        'status': 'livre'
    },
    {
        'id': 2,
        'nome_completo': 'Maria Pereira',
        'aniversario': '1985-09-23',
        'cargo': 'Operadora de Pulverizador',
        'salario': 2800.00,
        'equipamentos': ['pulverizador'],
        'data_admissao': '2021-04-15',
        'status': 'em_atividade'
    }
]




# Conexão com o banco de dados Oracle
#dsn = cx_Oracle.makedsn("oracle.fiap.com.br", 1521, service_name="ORCL")
#connection = cx_Oracle.connect(user='RM552051', password='140400', dsn=dsn)
#conn = cx_Oracle.connect(user='RM552051', password='140400', dsn=dsn)

# Local para salvar as imagens de upload
UPLOAD_FOLDER = './static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Página index 
@app.route('/')
def index():
    return render_template('index.html')



# Chave da API e URLs dos modelos do Roboflow
api_key = "pmgZQrQDbUTGDnTXIvNo"
model_endpoint_damage1 = "https://detect.roboflow.com/plants-disease-2599r/1"
model_endpoint_damage2 = "https://detect.roboflow.com/plants-final/1"
model_endpoint_pest = "https://detect.roboflow.com/pests-in-cucumber-plants-kcmdr/1"

# Análise de imagem via Roboflow (para doenças)
def analisar_imagem_roboflow_doenca(caminho_imagem):
    url_damage1 = f"{model_endpoint_damage1}?api_key={api_key}"
    url_damage2 = f"{model_endpoint_damage2}?api_key={api_key}"
    

    with open(caminho_imagem, "rb") as img_file:
        response1 = requests.post(url_damage1, files={"file": img_file})
        resultado1 = response1.json() if response1.status_code == 200 else None

    with open(caminho_imagem, "rb") as img_file:
        response2 = requests.post(url_damage2, files={"file": img_file})
        resultado2 = response2.json() if response2.status_code == 200 else None

    return resultado1, resultado2, 

# Análise de imagem via Roboflow (para pragas)
def analisar_imagem_roboflow_pragas(caminho_imagem):
    url_pest = f"{model_endpoint_pest}?api_key={api_key}"
    
    with open(caminho_imagem, "rb") as img_file:
        response_pest = requests.post(url_pest, files={"file": img_file})
        resultado_pragas = response_pest.json() if response_pest.status_code == 200 else None

    return resultado_pragas


# Rota para upload de imagem e análise de doenças 
@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'imagem' not in request.files:
            flash("Nenhuma imagem foi enviada.", "erro")
            return redirect(url_for('upload_page'))

        imagem = request.files['imagem']
        
        if imagem.filename == '':
            flash("Nenhuma imagem selecionada.", "erro")
            return redirect(url_for('upload_page'))

        caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], imagem.filename)
        imagem.save(caminho_imagem)

        resultado1, resultado2 = analisar_imagem_roboflow_doenca(caminho_imagem)

        return render_template('resultado.html',
                               imagem_filename=imagem.filename, 
                               resultado1=resultado1, 
                               resultado2=resultado2)

    return render_template('upload.html')


# Rota para upload de imagem e análise de pragas
@app.route('/analise_pragas', methods=['GET', 'POST'])
def analise_pragas_page():
    if request.method == 'POST':
        if 'imagem' not in request.files:
            flash("Nenhuma imagem foi enviada.", "erro")
            return redirect(url_for('analise_pragas_page'))

        imagem = request.files['imagem']
        if imagem.filename == '':
            flash("Nenhuma imagem selecionada.", "erro")
            return redirect(url_for('analise_pragas_page'))

        caminho_imagem = os.path.join(app.config['UPLOAD_FOLDER'], imagem.filename)
        imagem.save(caminho_imagem)
        
         
        resultado_pragas = analisar_imagem_roboflow_pragas(caminho_imagem)

        return render_template('resultado_pragas.html', imagem_filename=imagem.filename, resultado_pragas=resultado_pragas)

    return render_template('analise_pragas.html')


# Página de resultados das doenças
@app.route('/resultado')
def resultado():
    return render_template('resultado.html')

# Página de resultados das pragas
@app.route('/resultado_pragas')
def resultado_pragas():
    return render_template('resultado_pragas.html')


#####
##### MONITORAMENTO



###########
########### PLANTIO ###########





# Simulação de dados de áreas de plantio

# Rota para a Página com a lista de todas as áreas de plantio cadastradas

# Rota para fornecer dados das áreas de plantio

# Rota para a Página de cadastro de nova área de plantação

# Rota para a Página de cadastro de nova plantação 

# Rota para a Página com a lista de plantações cadastradas


# Rota para a Página para cadastrar novos funcionários


#######       ############
#######
#######
###### VER PLANTAÇÃO ###########
# Simular banco de dados de plantações no servidor
plantacoes_servidor = []

@app.route('/api/salvar_plantacao', methods=['POST'])
def salvar_plantacao():
    # Receber os dados enviados pelo front-end
    nova_plantacao = request.json
    plantacoes_servidor.append(nova_plantacao)  # Salvar a nova plantação no servidor (em memória)
    
    return jsonify({'status': 'sucesso', 'plantacao_id': nova_plantacao['id']})


@app.route('/api/ver_plantacao/<int:id>', methods=['GET'])
def ver_plantacao(id):
    # Buscar a plantação pelo ID
    plantacao = next((p for p in plantacoes_servidor), None)
    
    if plantacao:
        return jsonify(plantacao)  # Simulação: Retorna a plantação como JSON
    else:
        return "Plantação não encontrada", 404
    
@app.route('/ver_plantacao')
def ver_plantacao_page():
    return render_template('ver_plantacao.html')

@app.route('/nova_plantacao')
def nova_plantacao_page():
    return render_template('nova_plantacao.html')



@app.route('/areas_plantio', methods=['GET'])
def areas_plantio():
    return render_template('areas_plantio.html', plantacoes=plantacoes_servidor)









#######       ############
#######
#######
###### ESTOQUE ###########


# Rota para exibir o dashboard de controle de estoque, lucros e despesas
@app.route('/estoque')
def estoque_page():
    return render_template('estoque.html')


# Rota para fornecer dados do estoque
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    global estoque
    return jsonify({'estoque': estoque})

# Rota para cadastrar um novo insumo
# Simulação de banco de dados em memória
estoque_db = []

# Função para simular cálculo de lucro (ajuste conforme necessário)
def calcular_lucro(valor_unitario, quantidade):
    # Simulação: o lucro estimado é 20% do valor total
    lucro_estimado = valor_unitario * quantidade * 0.2
    return lucro_estimado

# Função para atualizar resumo de lucro e despesas
def atualizar_resumo():
    total_valor_pago = 0
    total_lucro_estimado = 0
    for item in estoque_db:
        total_valor_pago += item['valor_total']
        total_lucro_estimado += item['lucro_estimado']
    
    return {
        'total_valor_pago': total_valor_pago,
        'total_lucro_estimado': total_lucro_estimado
    }

# Rota para cadastrar novo item no estoque
@app.route('/api/cadastro_estoque', methods=['POST'])
def cadastrar_estoque():
    data = request.get_json()

    novo_item = {
        'descricao': data['descricao'],
        'tipo': data['tipo'],
        'tipo_especifico': data['tipo_especifico'],
        'quantidade': int(data['quantidade']),
        'valor_unitario': float(data['valor_unitario']),
        'valor_total': float(data['quantidade']) * float(data['valor_unitario']),
        'lucro_estimado': calcular_lucro(float(data['valor_unitario']), int(data['quantidade'])),
        'data_cadastro': datetime.now().strftime('%Y-%m-%d'),
        'data_expiracao': data['data_expiracao']
    }

    # Adiciona o novo item ao "banco de dados"
    estoque_db.append(novo_item)

    # Atualiza o resumo após o novo cadastro
    resumo_atualizado = atualizar_resumo()

    return jsonify({
        'message': 'Estoque cadastrado com sucesso!',
        'resumo': resumo_atualizado
    }), 201

# Rota para obter os dados do estoque e o resumo
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    # Retorna todos os itens do estoque e o resumo atualizado
    resumo = atualizar_resumo()
    return jsonify({
        'estoque': estoque_db,
        'resumo': resumo
    })


# Rota para excluir item do estoque
@app.route('/api/excluir_item/<int:index>', methods=['DELETE'])
def excluir_item(index):
    global estoque
    if 0 <= index < len(estoque):
        del estoque[index]  # Remove o item da lista com base no índice
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Item não encontrado'}), 404


# Rota para cadastrar um novo estoque

    # Calcula lucro estimado (simulação)
    lucro_por_tonelada = 200  # Exemplo de lucro por tonelada
    producao_estimada = quantidade / 20  # Supondo 20 kg/ha
    lucro_total_est = producao_estimada * lucro_por_tonelada
    global lucro_total
    lucro_total += lucro_total_est

    # Atualiza despesas
    despesa = {
        'descricao': f"Compra de {descricao}",
        'valor_despesa': gasto_total,
        'categoria': 'insumo'
    }
    despesas.append(despesa)
    global despesas_totais
    despesas_totais += gasto_total

    return jsonify({'success': True})

# Adicionando gráficos de desempenho financeiro
@app.route('/api/graficos_financeiros', methods=['GET'])
def graficos_financeiros():
    global lucro_total, despesas_totais
    dados_grafico = {
        'lucro_total': lucro_total,
        'despesas_totais': despesas_totais,
    }
    return jsonify(dados_grafico)


@app.route('/cadastro_estoque')
def cadastro_estoque():
    return render_template('cadastro_estoque.html')



#######
#######
####### EQUIPAMENTOS ###########

# Rota pagina equipamentos
@app.route('/equipamentos')
def equipamentos_page():
    return render_template('equipamentos.html')

# Gerador de ID simples
def gerar_id_equipamentos():
    if equipamentos:
        return max(equipamento['id'] for equipamento in equipamentos) + 1
    return 1

# Rota para listar os equipamentos
@app.route('/api/equipamentos', methods=['GET'])
def listar_equipamentos():
    return jsonify(equipamentos), 200

# Rota para cadastrar novo equipamento
@app.route('/api/equipamentos', methods=['POST'])
def add_equipamento():
    data = request.json
    cursor = conn.cursor()
     # Validação dos dados
    nome = data.get('nome')
    tipo = data.get('tipo')
    funcoes = data.get('funcoes')
    marca = data.get('marca')
    modelo = data.get('modelo')
    ano = data.get('ano')
    ultima_manutencao = data.get('ultima_manutencao')
    proxima_manutencao = data.get('proxima_manutencao')

    if not (nome and tipo and funcoes and marca and modelo and ano and ultima_manutencao and proxima_manutencao):
        return jsonify({"error": "Dados incompletos"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO equipamentos (nome, tipo, funcoes, marca, modelo, ano, ultima_manutencao, proxima_manutencao)
            VALUES (:nome, :tipo, :funcoes, :marca, :modelo, :ano, TO_DATE(:ultima_manutencao, 'YYYY-MM-DD'), TO_DATE(:proxima_manutencao, 'YYYY-MM-DD'))
        """, {
            'nome': nome,
            'tipo': tipo,
            'funcoes': funcoes,
            'marca': marca,
            'modelo': modelo,
            'ano': ano,
            'funcoes': funcoes,
            'ultima_manutencao': ultima_manutencao,
            'proxima_manutencao': proxima_manutencao
            
        })
        conn.commit()
    
    
    except not data:
        return jsonify({"error": "Dados inválidos"}), 400
    
    # Adicionar novo equipamento à lista em memória
    novo_equipamento = {
        "nome": data.get("nome"),
        "tipo": data.get("tipo"),
        "marca": data.get("marca"),
        "modelo": data.get("modelo"),
        "ano": data.get("ano"),
        "funcoes": data.get("funcoes", []),
        "status": "livre",
        "funcionario": None,
        "area_plantio": None,
        "ultima_manutencao": data.get("ultima_manutencao"),
        "proxima_manutencao": data.get("proxima_manutencao")
    }
    equipamentos.append(novo_equipamento)
    return jsonify({"message": "Equipamento cadastrado com sucesso"}), 201

# Rota para excluir equipamento (usando índice na lista como ID)
@app.route('/api/equipamentos/<int:id>', methods=['DELETE'])
def delete_equipamento(id):
    if id < 0 or id >= len(equipamentos):
        return jsonify({"error": "Equipamento não encontrado"}), 404
    equipamentos.pop(id)
    return jsonify({"message": "Equipamento removido com sucesso"}), 200








# Rota para gerenciamento de equipamentos


    # Calcular a próxima manutenção (6 meses após a última)
#    proxima_manutencao = datetime.strptime(ultima_manutencao, '%Y-%m-%d') + timedelta(days=180)

#    novo_equipamento = {
#        'id': gerar_id(),
#        'nome': nome,
#        'tipo': tipo,
#        'funcoes': funcoes,
#        'status': 'livre',  # Equipamento começa como "livre"
#        'funcionario': None,
#        'area_plantio': None,
#        'ultima_manutencao': ultima_manutencao,
#        'proxima_manutencao': proxima_manutencao.strftime('%Y-%m-%d')
#    }
    
     # Adicionar o novo equipamento à lista
#    equipamentos.append(novo_equipamento)
#    return jsonify({'message': 'Equipamento cadastrado com sucesso', 'equipamento': novo_equipamento}), 201

# Rota para atualizar o status do equipamento
@app.route('/api/equipamentos/<int:id>', methods=['PATCH'])
def atualizar_status_equipamento(id):
    data = request.json
    status = data.get('status')
    funcionario = data.get('funcionario')
    area_plantio = data.get('area_plantio')

    # Encontrar o equipamento pelo ID
    equipamento = next((equipamento for equipamento in equipamentos if equipamento['id'] == id), None)

    if not equipamento:
        return jsonify({'message': 'Equipamento não encontrado'}), 404

    # Atualizar o status
    if status:
        equipamento['status'] = status

    # Atualizar o funcionário e área de plantio, se necessário
    if status == 'em atividade':
        equipamento['funcionario'] = funcionario
        equipamento['area_plantio'] = area_plantio
    elif status == 'livre':
        equipamento['funcionario'] = None
        equipamento['area_plantio'] = None

    return jsonify({'message': 'Equipamento atualizado com sucesso', 'equipamento': equipamento}), 200


#######
#######
####### FUNCIONARIOS ###########
@app.route('/funcionarios')
def funcionarios_page():
    return render_template('funcionarios.html')



# Rota para a página de cadastro de novo funcionário
@app.route('/novo_funcionario', methods=['GET'])
def novo_funcionario():
    return render_template('cadastro_funcionario.html')



#######
#######
####### RESPONSABILIDADES funcionarios ###########
# Dados simulados para plantações, atividades ativas e realizadas
plantacoes = [
    {
        "nome": "Plantação A",
        "area_plantio": "5 hectares",
        "tipo_cultivo": "Soja",
        "atividades_realizadas": ["Aragem", "Colheita"],
        "equipamento_utilizado": "Trator"
    },
    {
        "nome": "Plantação B",
        "area_plantio": "3 hectares",
        "tipo_cultivo": "Milho",
        "atividades_realizadas": ["Poda", "Aplicação de Pesticida"],
        "equipamento_utilizado": "Pulverizador"
    }
]

atividades_ativas = [
    {
        "id": 1,
        "nome": "Aragem do Solo",
        "area_plantio": "5 hectares",
        "tipo": "Aragem",
        "equipamento": ["Trator"],
        "funcionario": "João da Silva",
        "data_maxima": "2024-09-30",
        "status": "pendente"
    },
    {
        "id": 2,
        "nome": "Poda de Milho",
        "area_plantio": "3 hectares",
        "tipo": "Poda",
        "equipamento": ["Semeadora"],
        "funcionario": "Maria Oliveira",
        "data_maxima": "2024-10-01",
        "status": "em_progresso"
    }
]

atividades_realizadas = [
    {
        "nome": "Colheita de Soja",
        "area_plantio": "5 hectares",
        "tipo": "Colheita",
        "equipamento": ["Colheitadeira"],
        "data_realizacao": "2024-09-15",
        "tempo_gasto": "4 horas",
        "observacoes": "Concluído com sucesso"
    },
    {
        "nome": "Aplicação de Pesticida no Milho",
        "area_plantio": "3 hectares",
        "tipo": "Aplicação de Pesticida",
        "equipamento": ["Pulverizador"],
        "data_realizacao": "2024-09-20",
        "tempo_gasto": "2 horas",
        "observacoes": "Tempo nublado, sem interferências"
    }
]

equipamentos_disponiveis = ["Trator", "Pulverizador", "Colheitadeira"]



@app.route('/responsabilidades')
def responsabilidades_page():
    return render_template('responsabilidades.html')

# Rota para retornar plantações
@app.route('/api/plantacoes', methods=['GET'])
def get_plantacoes():
    return jsonify(plantacoes)


# Rota para retornar atividades ativas
@app.route('/api/atividades_ativas', methods=['GET'])
def get_atividades_ativas():
    return jsonify(atividades_ativas)


# Rota para retornar atividades realizadas
@app.route('/api/atividades_realizadas', methods=['GET'])
def get_atividades_realizadas():
    return jsonify(atividades_realizadas)


# Rota para verificar disponibilidade de equipamentos
@app.route('/api/equipamentos_disponiveis', methods=['GET'])
def get_equipamentos_disponiveis():
    return jsonify(equipamentos_disponiveis)


# Rota para fazer check-in
@app.route('/api/checkin/<int:id>', methods=['POST'])
def checkin(id):
    # Verificar se o ID da atividade existe
    atividade = next((a for a in atividades_ativas if a['id'] == id), None)
    if not atividade:
        return jsonify({'error': 'Atividade não encontrada'}), 404

    # Simulando a verificação do equipamento
    indisponiveis = [equip for equip in atividade['equipamento'] if equip not in equipamentos_disponiveis]
    if indisponiveis:
        return jsonify({'error': 'Equipamento indisponível', 'equipamento': indisponiveis}), 400

    # Simulando a alteração do status para "em progresso"
    atividade['status'] = 'em_progresso'
    return jsonify({'message': 'Check-in realizado com sucesso'}), 200


# Rota para fazer check-out
@app.route('/api/checkout/<int:id>', methods=['POST'])
def checkout(id):
    # Verificar se o ID da atividade existe
    atividade = next((a for a in atividades_ativas if a['id'] == id), None)
    if not atividade:
        return jsonify({'error': 'Atividade não encontrada'}), 404

    data = request.get_json()
    tipo_checkout = data.get('tipoCheckout', 'concluida')
    observacoes = data.get('observacoes', '')

    # Simular o checkout e mover para atividades realizadas se for concluída
    if tipo_checkout == 'concluida':
        atividade_realizada = {
            "nome": atividade['nome'],
            "area_plantio": atividade['area_plantio'],
            "tipo": atividade['tipo'],
            "equipamento": atividade['equipamento'],
            "data_realizacao": "2024-09-25",  # Data simulada
            "tempo_gasto": "3 horas",  # Simulando tempo gasto
            "observacoes": observacoes or "N/A"
        }
        atividades_realizadas.append(atividade_realizada)
        atividades_ativas.remove(atividade)
        return jsonify({'message': 'Atividade concluída com sucesso'}), 200
    elif tipo_checkout == 'pausa':
        atividade['status'] = 'pendente'
        return jsonify({'message': 'Atividade pausada com sucesso'}), 200
    else:
        return jsonify({'error': 'Tipo de checkout inválido'}), 400


# Rota para cadastrar nova atividade
@app.route('/api/atividades', methods=['POST'])
def cadastrar_atividade():
    data = request.get_json()

    nova_atividade = {
        "id": len(atividades_ativas) + 1,
        "nome": data['nomeAtividade'],
        "area_plantio": data['plantacaoSelecionada'],
        "tipo": data['tipoAtividade'],
        "equipamento": [data['equipamento']],
        "funcionario": "João da Silva",  # Exemplo fixo de funcionário
        "data_maxima": data['dataRealizacao'],
        "status": "pendente"
    }

    atividades_ativas.append(nova_atividade)
    return jsonify({'message': 'Atividade cadastrada com sucesso!'}), 201


#######
#######
####### RESPONSABILIDADES funcionarios ###########


# Endpoint para obter a lista de funcionários
@app.route('/api/funcionarios', methods=['GET'])
def get_funcionarios():
    return jsonify(funcionarios)




#######
#######
####### PLANTAÇÃO ###########
@app.route('/plantacao', methods=['GET'])
def plantacao_page():
    return render_template('plantacao.html')

# Rota para cadastro de plantação
@app.route('/api/plantacao', methods=['POST'])


@app.route('/nova_plantacao', methods=['GET'])
def nova_plantacao():
    return render_template('nova_plantacao.html')



#######
#######
####### FINANCEIRO ###########
@app.route('/financeiro')
def financeiro_page():
    return render_template('financeiro.html')




#######
#######
####### CRONOGRAMA ###########
@app.route('/cronograma')
def cronograma_page():
    return render_template('cronograma.html')

# Rota para cadastro de cronograma de plantação
@app.route('/api/cronograma', methods=['POST'])


#######
#######
####### LOGISTICA ###########
@app.route('/logistica')
def logistica_page():
    return render_template('logistica.html')

# Rota para gerenciamento de logística
@app.route('/api/logistica', methods=['POST'])


# Rota para cadastro de entrega de logística
@app.route('/api/entrega', methods=['POST'])





#######
#######
####### ATIVIDADES ###########


# Rota para cadastro de atividades
@app.route('/api/atividades', methods=['POST'])

@app.route('/atividades')
def atividades_page():
    return render_template('atividades.html')

# Dados temporários para simular o banco de dados
atividades_concluidas = [
    {"id": 2, "nome": "Colheita", "area_plantio": "Área 2", "tipo": "Colheita", "equipamento": ["Colheitadeira"], "funcionario": "Maria", "data_realizacao": "2024-09-22", "tempo_gasto": "2 horas"},
    
]





@app.route('/drone_ia')
def drone_ia():
    return render_template('drone_ia.html')



if __name__ == '__main__':
        app.run(debug=True, port=8080)

