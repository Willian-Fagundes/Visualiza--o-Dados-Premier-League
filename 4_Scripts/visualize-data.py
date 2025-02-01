import streamlit as st 
import requests
import json
import pandas as pd
from pandas import json_normalize
from io import StringIO
from sqlalchemy import create_engine
import plotly.express as px
import random
import plotly.figure_factory as ff
import plotly.graph_objects as go

st.title("Dados da temporada 23/24 Premier League")

engine = create_engine('sqlite:////Users/estudo/Documents/Projeto/0_Bases_Tratadas/premier.db', echo =True)

connection = engine.connect()

dados = pd.read_sql('SELECT * FROM Dados', con = engine)

times = dados['Time_Casa'].sort_values(ascending=True).unique()

classificacao = pd.read_sql('SELECT * FROM "Classificação 38"', con=engine)

cores = ["#636EFA", "#EF553B", "#00CC96"]
cores1 = ["#636EFA", "#00CC96"]

pontos = classificacao[["Times","Pontos"]]
pontos["Aproveitamento"] = (pontos["Pontos"] / 114 * 100).round(2)



fig_pontos = px.bar(pontos, 
                    x="Times", 
                    y= ["Pontos","Aproveitamento"],
                    barmode="group",
                    text_auto=True)
fig_pontos.update_traces(textposition = 'outside')
for i, trace in enumerate(fig_pontos.data):
    trace.marker.color = cores1[i]


fig_partidas = px.bar(classificacao, x = "Times", y = ["Partidas_Vencidas", "Partidas_Perdidas", "Empates"], barmode= 'group', text_auto= True)
fig_partidas.update_traces(textposition='outside', width= 0.3)
for i, trace in enumerate(fig_partidas.data):
    trace.marker.color = cores[i]


gols_marcados = classificacao[["Times", "Gols_Marcados", "Gols_Sofridos", "Saldo_de_Gols"]]
fig_gols = px.bar(gols_marcados, x = "Times", y = ["Gols_Marcados", "Gols_Sofridos", "Saldo_de_Gols"], barmode='group', text_auto=True)
fig_gols.update_traces(textposition = 'outside')
for i, trace in enumerate(fig_gols.data):
    trace.marker.color = cores[i]


def partidas (time):
    cores = ["#636EFA", "#EF553B", "#00CC96"]
    dados = pd.read_sql("SELECT * FROM 'Classificação 38'", con = engine)
    partida = dados.loc[dados["Times"] == time]
    partida_final = partida[["Times", "Partidas_Vencidas", "Partidas_Perdidas", "Empates"]]

    fig = px.bar(partida_final, x = "Times", y = ["Partidas_Vencidas", "Partidas_Perdidas", "Empates"], barmode= 'group', text_auto= True,
                 height= 490)
    fig.update_traces(textposition='outside', width= 0.3)
    fig.update_layout(
    xaxis_title="",  # Remove o rótulo do eixo X
    yaxis_title=""
    )
    for i, trace in enumerate(fig.data):
        trace.marker.color = cores[i]
    

    return fig

def saldo_gols (time):
    dados = pd.read_sql("SELECT * FROM 'Classificação 38'", con = engine)
    gols_marcados = dados[["Times", "Gols_Marcados", "Gols_Sofridos", "Saldo_de_Gols"]]
    gols_time = dados.loc[dados["Times"] == time]
    gols_final = gols_time[["Times", "Gols_Marcados", "Gols_Sofridos", "Saldo_de_Gols"]]
    fig = px.bar(gols_final, x = "Times", y = ["Gols_Marcados", "Gols_Sofridos", "Saldo_de_Gols"], barmode='group', text_auto=True, height= 495)
    fig.update_traces(textposition = 'outside')
    for i, trace in enumerate(fig.data):
        trace.marker.color = cores[i]
    return fig


def pos_time (time):
    rodadas = []
    gols = []
    for i in range(1,39):
        tabela_posicao = pd.read_sql(f'SELECT * FROM "Classificação {i}"', con = engine)
        rodadas.append(tabela_posicao)   
    
    for rodadas_index, rodada in enumerate(rodadas, start= 1):
        posicao = rodada[rodada["Times"] == time].index[0] +1
        gols.append(posicao)
    golsdf = pd.DataFrame(gols)
    golsdf = golsdf.rename(columns={0: "Pos"})
    golsdf = golsdf.reset_index(drop=True)
    golsdf.index = golsdf.index + 1
    fig = px.line(golsdf, x = golsdf.index, y = 'Pos', markers= True, title=f'Desempenho {selecionar}')
    fig.update_layout(
        yaxis=dict(range=[20,1], dtick =1,title=dict(
            text="Posição"
        )),

        xaxis=dict(
            range=[1, 38],
            tickmode='linear',
            dtick=1, title=dict(
            text="Rodadas"
        )))
    return fig

def saldogols(time):
    rodadas = []
    saldo_gols = []
    gols_feitos = []
    gols_sofridos = []
    for i in range(1,39):
        tabela_posicao = pd.read_sql(f'SELECT * FROM "Classificação {i}"', con = engine)
        rodadas.append(tabela_posicao) 
        saldo_gol = tabela_posicao.loc[tabela_posicao["Times"] == time, "Saldo_de_Gols"]
        gol_marcado = tabela_posicao.loc[tabela_posicao["Times"] == time, "Gols_Marcados"]
        gol_sofrido = tabela_posicao.loc[tabela_posicao["Times"] == time, "Gols_Sofridos"]
        saldo_gols.append(saldo_gol)
        gols_feitos.append(gol_marcado)
        gols_sofridos.append(gol_sofrido)

    gols_feitosdf = pd.DataFrame(gols_feitos)
    gols_sofridosdf = pd.DataFrame(gols_sofridos)
    saldo_golsdf = pd.DataFrame(saldo_gols)

    saldo_golsdf['Saldo_de_Gols'] = saldo_golsdf.apply(lambda row: row.dropna().values[0] if len(row.dropna()) > 0 else None, axis=1)
    gols_feitosdf['Gols_Marcados'] = gols_feitosdf.apply(lambda row: row.dropna().values[0] if len(row.dropna()) > 0 else None, axis=1)
    gols_sofridosdf['Gols_Sofridos'] = gols_sofridosdf.apply(lambda row: row.dropna().values[0] if len(row.dropna()) > 0 else None, axis=1)

    saldo_golsdf = saldo_golsdf[["Saldo_de_Gols"]]
    saldo_golsdf = saldo_golsdf.reset_index(drop = True)
    saldo_golsdf.index = saldo_golsdf.index + 1

    gols_feitosdf = gols_feitosdf[["Gols_Marcados"]]
    gols_feitosdf = gols_feitosdf.reset_index(drop = True)
    gols_feitosdf.index = gols_feitosdf.index + 1

    gols_sofridosdf = gols_sofridosdf[["Gols_Sofridos"]]
    gols_sofridosdf = gols_sofridosdf.reset_index(drop = True)
    gols_sofridosdf.index = gols_sofridosdf.index + 1

    consolidado = pd.concat([gols_feitosdf,gols_sofridosdf,saldo_golsdf], axis= 1 )

    fig = px.line(consolidado, x = consolidado.index, y = ['Gols_Marcados', 'Gols_Sofridos', 'Saldo_de_Gols'])
    fig.update_layout(
        title= f"Gols Marcados x Gols Sofridos x Saldo de gols {selecionar}",
        legend_title="",
        yaxis = dict (title=dict(
            text="Gols")),
        xaxis=dict(range=[1, 38],
            tickmode='linear',
            dtick=1, title=dict(
            text="Rodadas")))

    return fig

def posicao_final(time):
    classificacao = pd.read_sql('SELECT * FROM "Classificação 38"', con=engine)
    pos_final = classificacao.loc[classificacao["Times"] == time].index[0] + 1
    return pos_final

def partidas_casa(time):
    tabela_time = pd.read_sql(f'SELECT * FROM {time}', con = engine)
    time_casa = tabela_time[tabela_time["Time_Casa"] == time]
    def substituir_resultado(valor):
        if valor == time:
            return 'Vitória'
        elif valor == 'Empate':
            return 'Empate'
        else:
            return 'Derrota'


    time_casa['Vencedor'] = time_casa['Vencedor'].apply(substituir_resultado)

    resultados = time_casa["Vencedor"].value_counts()

    fig = px.bar(resultados, text_auto=True, height= 495) 
    fig.update_traces(textposition='outside', width= 0.3)
    fig.update_layout(
    xaxis_title="",
    yaxis_title=""
    )
    for i, trace in enumerate(fig.data):
        trace.marker.color = cores[i]
    
    return fig


tab1, tab2= st.tabs(["Estatisticas do Campeonato","Estatisticas dos Times"])



with tab1:
    st.plotly_chart(fig_pontos)
    st.plotly_chart(fig_gols)
    st.plotly_chart(fig_partidas)

with tab2:
    st.markdown("Selecione um Time")
    selecionar = st.selectbox("Times", times)
    dados = pd.read_sql("SELECT * FROM 'Classificação 38'", con = engine)
    pontos = dados[["Times","Pontos"]]
    pontos["Aproveitamento"] = (pontos["Pontos"] / 114 * 100).round(2)
    media = round(pontos["Aproveitamento"].mean(), 2)
    aproveita = pontos.loc[pontos["Times"] == selecionar, "Aproveitamento"].values[0]
    diferenca = round(aproveita - media, 2)

    if aproveita >= diferenca:
        color = 'normal'
    else:
        color = "inverse"


    df_times = dados[["Times", "Gols_Marcados"]]
    df_times["media_gols"] = (dados["Gols_Marcados"]/38).round(2)
    media_gol = (df_times["media_gols"].sum()/20).round(2)
    media_time = df_times.loc[df_times["Times"] == selecionar, "media_gols"].sum()
    gols_max = df_times["media_gols"].max()
    diferenca_gols = round(media_time - media_gol,2)
    

    tabela_time_casa = pd.read_sql(f'SELECT * FROM {selecionar}', con = engine)
    time_casa = tabela_time_casa[tabela_time_casa["Time_Casa"] == selecionar]
    def substituir_resultado(valor):
        if valor == selecionar:
            return 'Vitória'
        elif valor == 'Empate':
            return 'Empate'
        else:
            return 'Derrota'

    time_casa['Vencedor'] = time_casa['Vencedor'].apply(substituir_resultado)
    vencedor_casa = time_casa['Vencedor']
    vencedor_casa_df = pd.DataFrame(vencedor_casa)
    pontos_vitoria_casa = (vencedor_casa_df['Vencedor'] == 'Vitória').sum() * 3
    pontos_empate_casa = (vencedor_casa_df['Vencedor'] == 'Empate').sum()
    pontos_totais_casa = pontos_vitoria_casa + pontos_empate_casa
    aproveitamento_casa = round(pontos_totais_casa / 57 * 100, 2)


    with st.expander("Dados Gerais"):
        with st.container():
            st.metric(label = "Posição final", value= f"{posicao_final(selecionar)}º")
            col1, col2 = st.columns(2)
            with col1:
            
                st.metric(label= "Aproveitamento", value= f"{aproveita}%", delta= f"{diferenca}%", delta_color = color,
                      label_visibility= 'visible')
                st.plotly_chart(partidas(selecionar))
            
            with col2:
                st.metric(label = "Media de Gols",value = media_time, delta= diferenca_gols)
           
                st.plotly_chart(saldo_gols(selecionar))

        st.write(pos_time(selecionar))
        st.plotly_chart(saldogols(selecionar), key = 'Unique_Key_02')

    with st.expander("Dados como Mandante"):
        st.metric(label='Aproveitamento', value = f'{aproveitamento_casa}%')
        st.plotly_chart(partidas_casa(selecionar))
        