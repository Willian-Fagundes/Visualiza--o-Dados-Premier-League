import pandas as pd
import sqlite3
from sqlite3 import Cursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

#Criar um DB para armazenar tabelas dos times
engine = create_engine('sqlite:////Users/estudo/Documents/Visualização-Dados-Premier-League/0_Bases_Tratadas/premier.db', echo =True)

connection = engine.connect()

#Preparar os dados para serem armazenados em um DB

dados = pd.read_csv('/Users/estudo/Documents/Visualização-Dados-Premier-League/1_Bases_Originais/premier_league_24_25.csv', sep = ';')

#Adicionar uma nova coluna com o vencedor/perdedor

def resultado (time):

    if time['Gols_Casa'] > time['Gols_Visita']:
        return time['Time_Casa']
    elif time['Gols_Casa'] < time['Gols_Visita']:
        return time['Time_Visita']
    else:
        return 'Empate'
    
dados['Vencedor'] = dados.apply(resultado, axis=1)

dados['Time_Casa'] = dados["Time_Casa"].str.replace(' ', '')
dados['Time_Visita'] = dados["Time_Visita"].str.replace(' ', '')
dados['Vencedor'] = dados['Vencedor'].str.replace(' ','')

dados.to_sql('Dados', con  = engine, if_exists='replace', index=False)


Teams = dados['Time_Casa'].unique()
dfteams = pd.DataFrame(Teams, columns= ['Times'])
dfteams = dfteams.sort_values(by=['Times'], ascending= True)
dfteams = dfteams.reset_index(drop=True)
dfteams

#Criar tabelas unicas para cada time para que possam ser tratados de forma individual

for i in dfteams['Times'].unique():
    jogos_casa = dados[dados['Time_Casa'] == i]
    jogos_fora = dados[dados['Time_Visita'] == i]
    tabela_time = pd.concat([jogos_casa, jogos_fora])
    tabela_time.reset_index(drop=True, inplace=True)
    tabela_time.to_sql(i, con  = engine, if_exists='replace', index=False)

#Criar tabelas unicas por Rodada 1 - 38

for j, inicio in enumerate(range(0, len(dados), 10), start=1):
    
    rodadas = dados.iloc[inicio:inicio+10]
    nome_rodada = f"Rodada {j}" 
    rodadas.to_sql(nome_rodada, con  = engine, if_exists='replace', index=False)

# Tabela de classificação a cada rodada 1 - 38

rodada_atual = nome_rodada.replace('Rodada', '').replace(' ','')
rodada_atual = int(rodada_atual)
rodada_atual

#Adicionar os pontos de classificação

dfteams["Posição"] = range(1, 21)
dfteams["Times"] = dados['Time_Casa'].unique()
dfteams["Partidas_Jogadas"] = 0
dfteams["Partidas_Vencidas"] = 0
dfteams["Empates"] = 0
dfteams["Partidas_Perdidas"] = 0
dfteams["Gols_Marcados"] = 0
dfteams["Gols_Sofridos"] = 0
dfteams["Saldo_de_Gols"] = dfteams["Gols_Marcados"] - dfteams["Gols_Sofridos"]
dfteams["Impedimentos"] = 0
dfteams["Faltas_Cometidas"] = 0
dfteams["Faltas_Sofridas"] = 0
dfteams["Pontos"] = 0
dfteams = dfteams.sort_values(by= ["Pontos", "Saldo_de_Gols", "Gols_Marcados","Gols_Sofridos","Impedimentos","Faltas_Sofridas","Faltas_Cometidas"], ascending= [False,False,False,True,True,False,True])
dfteams = dfteams.reset_index(drop=True)
dfteams = dfteams.set_index("Posição")

for x in range(1, rodada_atual + 1):
    time = pd.read_sql(f"SELECT * FROM 'Rodada {x}'", con = engine)

    for _, row in time.iterrows():
        time_casa = row["Time_Casa"]
        time_visita = row["Time_Visita"]
        gols_casa = row["Gols_Casa"]
        gols_visita = row["Gols_Visita"]
        impedimentos_casa = row["impedimentos_casa"]
        impedimentos_visita = row["impedimentos_visita"]
        faltas_sofridas =row["faltas_cometidas_visita"]
        faltas_cometidas = row["faltas_sofridas_casa"]
        vencedor = row["Vencedor"]
        #loop do vencedor
        if vencedor == time_casa:  # Time da casa venceu
            dfteams.loc[dfteams["Times"] == time_casa, "Pontos"] += 3
        elif vencedor == time_visita:  # Time visitante venceu
            dfteams.loc[dfteams["Times"] == time_visita, "Pontos"] += 3
        elif vencedor == "Empate":  # Empate
            dfteams.loc[dfteams["Times"] == time_casa, "Pontos"] += 1
            dfteams.loc[dfteams["Times"] == time_visita, "Pontos"] += 1
        #loop dos gols marcados e sofridos
        if time_casa in dfteams["Times"].values:
            dfteams.loc[dfteams["Times"] == time_casa, "Gols_Marcados"] += gols_casa
            dfteams.loc[dfteams["Times"] == time_casa, "Gols_Sofridos"] += gols_visita
            dfteams.loc[dfteams["Times"] == time_visita, "Gols_Sofridos"] += gols_casa
            dfteams.loc[dfteams["Times"] == time_visita, "Gols_Marcados"] += gols_visita
            dfteams["Saldo_de_Gols"] = dfteams["Gols_Marcados"] - dfteams["Gols_Sofridos"]
        #loop de impedimentos
        if time_casa in dfteams["Times"].values:
            dfteams.loc[dfteams["Times"] == time_casa, "Impedimentos"] += impedimentos_casa
            dfteams.loc[dfteams["Times"] == time_visita, "Impedimentos"] += impedimentos_visita
        #loop de faltas
        if time_casa in dfteams["Times"].values:
            dfteams.loc[dfteams["Times"] == time_casa, "Faltas_Cometidas"] += faltas_cometidas
            dfteams.loc[dfteams["Times"] == time_visita, "Faltas_Sofridas"] += faltas_sofridas
        #loop de partidas jogadas
        if time_casa in dfteams["Times"].values:
            dfteams.loc[dfteams["Times"] == time_casa, "Partidas_Jogadas"] += 1
            dfteams.loc[dfteams["Times"] == time_visita, "Partidas_Jogadas"] += 1
        #loop de partidas perdidas, vencidas ou empates
        if time_casa in dfteams["Times"].values:
            dfteams.loc[dfteams["Times"] == vencedor, "Partidas_Vencidas"] += 1
        if row["Vencedor"] == "Empate":
            time_casa = row["Time_Casa"]
            time_visita = row["Time_Visita"]

            # Incrementar partidas empatadas para time_casa
            if time_casa in dfteams["Times"].values:
                dfteams.loc[dfteams["Times"] == time_casa, "Empates"] += 1

        # Incrementar partidas empatadas para time_visitante
            if time_visita in dfteams["Times"].values:
                dfteams.loc[dfteams["Times"] == time_visita, "Empates"] += 1
        if row["Vencedor"] == time_casa:
            dfteams.loc[dfteams["Times"] == time_visita, "Partidas_Perdidas"] += 1
        if row["Vencedor"] == time_visita:
            dfteams.loc[dfteams["Times"] == time_casa, "Partidas_Perdidas"] += 1
        
        
        
            
        
        rodada_class = f"Classificação {x}"
        dfteams = dfteams.sort_values(by= ["Pontos", "Saldo_de_Gols", "Gols_Marcados","Gols_Sofridos","Impedimentos","Faltas_Sofridas","Faltas_Cometidas"], ascending= [False,False,False,True,True,False,True])
        dfteams = dfteams.reset_index(drop=True)
       
        dfteams.to_sql(rodada_class, con  = engine, if_exists='replace', index=False)

class_atual = "Classificação Atual"
dfteams = dfteams.sort_values(by= ["Pontos", "Saldo_de_Gols", "Gols_Marcados","Gols_Sofridos","Impedimentos","Faltas_Sofridas","Faltas_Cometidas"], ascending= [False,False,False,True,True,False,True])
dfteams = dfteams.reset_index(drop=True)
       
dfteams.to_sql(class_atual, con  = engine, if_exists='replace', index=False)


