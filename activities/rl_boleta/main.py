# from training import train_agent
from training import train_agent
from testing import test_agent
import csv
from datetime import datetime
import pdb

# IR MODIFICANDO A QUANTIDADE DE DIAS (TOTAL DE 7 PARA O DATAFRAME DE TESTE)
DIAS_TESTE = 7

header = ['run', 'base de treinamento', 'passos de treinamento', 'numero da iteracao', 'treinamento - condição de parada', 'quantidade de episódios terminais treino', \
'recompensas treino', 'valor inicial treino', 'valor final treino', 'lucro/prejuízo treino', 'base de teste', 'quantidade de dias', \
'numero da iteracao teste', 'quantidade de episódios teste', 'recompensas teste', 'valor inicial teste', 'valor final teste', 'lucro/prejuízo teste', \
'quantidade de passos teste']
files_training = ['consolidado_treinamento (01.12 a 06.12).csv', 'consolidado_treinamento (10.01 a 14.01).csv', \
    'consolidado_treinamento (18.01 a 26.01).csv', 'consolidado_treinamento (21.02 a 11.03).csv', \
    'consolidado_treinamento (23.03 a 28.03).csv', 'consolidado_treinamento (07.04 a 15.04).csv',
    'consolidado_treinamento (18.04 a 29.04).csv']


# files_testing = ['consolidado_treinamento (21.02 a 11.03).csv']
# files_testing = ['consolidado_treinamento (23.03 a 28.03).csv']
# files_testing = ['consolidado_treinamento (07.04 a 15.04).csv']
# files_testing = ['consolidado_treinamento (18.04 a 29.04).csv']
files_testing = ['consolidado_teste (02.05 a 13.05).csv']


string_now = datetime.now().strftime('%d_%m_%Y_%H:%M:%S')


# Laço iterativo para realizar 30 treinamentos e testes, para cada quantidade de timesteps
for j in range(10):
    results_training = train_agent(files_training, j)

    results_testing = test_agent(files_testing[0], DIAS_TESTE, j)
    
    run = {'run': j + 1}
    
    results = {**run, **results_training, **results_testing}
    # results = {**run, **results_training}
    # results = {**run, **results_testing}

    if j == 0:
        mode = 'w'
    else:
        mode = 'a'

    with open(f'./results/{string_now}.csv', mode, encoding='UTF8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if j == 0:
            writer.writeheader()
        writer.writerow(results)


# Iteração nos testes (mínimo 30)
# Quantidade de dias de operação do agente (horizontes temporais diferentes - 5, 10 e 15 dias?)
# Treinos em separado e treinos com arquivos seguidos (caso feche os outros pontos com sucesso, e se fizer sentido)
# Plotar o gráfico de recompensas com o delay modifier, para o treinamento
