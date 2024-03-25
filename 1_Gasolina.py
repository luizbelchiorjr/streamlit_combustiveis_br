import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.validators.scatter.marker import SymbolValidator
import json
from urllib.request import urlopen
from PIL import Image

st.set_page_config(layout= 'wide')

produto = 'GASOLINA'

@st.cache_data
def load_data():

    df = pd.read_csv('./data/df_states.csv', sep= ';')
    df_years = pd.read_csv('./data/df_years.csv', sep= ';')
    df_comparativo_geral = pd.read_csv('./data/df_comparativo_geral.csv', sep= ';')
    df_comparativo_states = pd.read_csv('./data/df_comparativo_states.csv', sep= ';')
    df_comparativo_citys = pd.read_csv('./data/df_comparativo_citys.csv', sep= ';')
    df_map = pd.read_csv('./data/df_map.csv', sep= ';')
    geojson = json.load(open('./data/brasil_estados.json'))

    return df, df_years, df_comparativo_geral, df_comparativo_citys, df_comparativo_states, df_map, geojson

df, df_years, df_comparativo_geral, df_comparativo_citys, df_comparativo_states, df_map, geojson = load_data()

df_years['ANO'] = df_years['ANO'].astype(str)

# Reset filtro
def reset():
        st.session_state['city_select_key'] = None

# Line_1 - Cards

def line_1():

    # Values Cards
    # medias/ano
    mean_22 = df_years[
        (df_years['ANO'] == '2022') &
        (df_years['PRODUTO'] == produto)
        ]['VL_MEDIO_VENDA'].tolist()[0]
    

    mean_23 = df_years[
        (df_years['ANO'] == '2023') &
        (df_years['PRODUTO'] == produto)
        ]['VL_MEDIO_VENDA'].tolist()[0]

    # VL Mínimos
    vl_min_22 = df_years[
        (df_years['ANO'] == '2022') &
        (df_years['PRODUTO'] == produto)
        ]['VL_MIN_VENDA'].tolist()[0]
    
    vl_min_23 = df_years[
        (df_years['ANO'] == '2023') &
        (df_years['PRODUTO'] == produto)
        ]['VL_MIN_VENDA'].tolist()[0]

    # VL Máximos
    vl_max_22 = df_years[
        (df_years['ANO'] == '2022') &
        (df_years['PRODUTO'] == produto)
        ]['VL_MAX_VENDA'].tolist()[0]
    
    vl_max_23 = df_years[
        (df_years['ANO'] == '2023') &
        (df_years['PRODUTO'] == produto)
        ]['VL_MAX_VENDA'].tolist()[0]

    # Qt coletado
    qt_coleta_22 = df_years[
        (df_years['ANO'] == '2022') &
        (df_years['PRODUTO'] == produto)
        ]['QT_COLETADO'].tolist()[0]
    
    qt_coleta_23 = df_years[
        (df_years['ANO'] == '2023') &
        (df_years['PRODUTO'] == produto)
        ]['QT_COLETADO'].tolist()[0]

    # Cards
    lista_value_cards = [
        qt_coleta_22,
        mean_22,
        vl_min_22,
        vl_max_22,
        qt_coleta_23,
        mean_23,
        vl_min_23,
        vl_max_23
    ]
    
    title_cards = [
        'Qtde Amostra<br>2022',
        'Valor médio<br>2022',
        'Valor mínimo<br>2022',
        'Valor máximo<br>2022',
        'Qtde Amostra<br>2023',
        'Valor médio<br>2023',
        'Valor mínimo<br>2023',
        'Valor máximo<br>2023'
    ]
    
    mode_cards = ['number', 'number', 'number', 'number', 'number+delta', 'number+delta', 'number+delta', 'number+delta']
    preffixs = ['', 'R$', 'R$', 'R$', '', 'R$', 'R$', 'R$']
    rows = [1,1,1,1,2,2,2,2]
    cols = [1,2,3,4,1,2,3,4]
    values_formats = ['i', 'f', 'f', 'f', 'i', 'f', 'f', 'f']
    deltas = [0,0,0,0, qt_coleta_22, mean_22, vl_min_22, vl_max_22]

    cards = make_subplots(
        rows=2,
        cols=4,
        specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}],
        [{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]],
        row_heights=[1, 1],  # Adicionado para garantir alturas proporcionais
        column_widths=[1, 1, 1, 1]  # Adicionado para garantir larguras proporcionais
    )

    for value, title, col, mode, delta_, row, prefix, values_format in zip(lista_value_cards, title_cards, cols, mode_cards, deltas, rows, preffixs, values_formats):

        # Config
        font_size_title= 23.5            
        config_font_number = dict(font_color= 'black',
                                font_size= 25,
                                valueformat = values_format)

        cards.add_trace(
            go.Indicator(
                    mode= mode,
                    title= {'text': '<b>{}</b>'.format(title),
                            'font_color': 'black',
                            'font_size': font_size_title},
                    value = value,
                    number = config_font_number,
                    number_prefix= prefix,
                    align = 'center',
                    delta= dict(reference= delta_,
                                valueformat= 'i',
                                font= dict(size= 21))
                ), row, col)

        cards.update_layout(height= 450)
    
    st.plotly_chart(cards, use_container_width= True)

# Line 2 - Mapa

def line_2():

    col1, colx, col2 = st.columns([1.7, 0.2, 1])

    with col1:

        mapa_image = Image.open('./assets/mapa_{}.png'.format(produto))
        st.image(mapa_image)

    with col2:

        st.dataframe(
            data= df_map[df_map['PRODUTO'] == produto][['NM_ESTADO', 'PRODUTO', 'VL_MEDIO_VENDA']].sort_values('VL_MEDIO_VENDA', ascending= False).rename(
                columns= {'VL_MEDIO_VENDA': 'VL_MEDIO_VENDA (R$)'}
            ),
            width= 500,
            height= 425,
              use_container_width= False,
                hide_index= True,
                
                )
        
        st.markdown("<span style='text-align: center; color: black;'>Tabela - Valor Médio Estados - {}<br>Fonte: dados.gov</span>".format(produto), unsafe_allow_html=True)

# Line 3 - Comparativo Anual
def line_3():

    # Comparativo Anual
    # config        
    colors_comp = ['#149000', '#f0dc00']
    years = df_comparativo_geral['ANO'].unique()
    mode= 'lines+markers+text'

    states = df_comparativo_states['NM_ESTADO'].sort_values().unique().tolist()
    states.insert(0, 'TODOS')

    # Estado e município
    col1, col2 = st.columns(2)

    with col1:
        # Selecbox Estado
        state_select = st.selectbox(
            'Selecione o Estado (opcional)',
            states,
            index= 0,
            key= 'state_select_key'
        )

    with col2:
        # Selecbox Estado
        city_select = st.selectbox(
            'Selecione o município',
            df_comparativo_citys[df_comparativo_citys['NM_ESTADO'] == state_select]['MUNICIPIO'].sort_values().unique().tolist(),
            index= None,
            key= 'city_select_key',
            placeholder= 'Opcional'
        )

        reset_button = st.button('Remover filtro', on_click= reset)

    # Condição estado == todos
    if state_select == 'TODOS':

        # 2022
        comp_graph = go.Figure()

        comp_graph.add_trace(
            go.Scatter(
                x= df_comparativo_geral[(df_comparativo_geral['ANO'] == years[0]) & (df_comparativo_geral['PRODUTO'] == produto)]['NM_MES'],
                y= df_comparativo_geral[(df_comparativo_geral['ANO'] == years[0]) & (df_comparativo_geral['PRODUTO'] == produto)]['VL_MEDIO_VENDA'],
                marker_color= colors_comp[0],
                hovertext = "R$ " + df_comparativo_geral[(df_comparativo_geral['ANO'] == years[0]) & (df_comparativo_geral['PRODUTO'] == produto)]['VL_MEDIO_VENDA'].apply(lambda x: str(x)),
                hoverinfo= 'text',
                mode= mode,
                name = '{}'.format(years[0])
            )
        )   
        
        comp_graph.update_layout(
        barmode= 'group',
        template= 'simple_white',
        legend= dict(
            orientation= 'h',
            font= dict(size= 15),
            x= 0.425,
            y= 1.225),
        height= 525,
        hoverlabel= dict(
            font= dict(color= 'white',
                        size= 14),
            bgcolor= 'black')
    )

        comp_graph.update_xaxes(tickfont=dict(color='black', size= 14),
                        tickcolor= 'black'
                        #tickangle= -10
                        )

        comp_graph.update_yaxes(tickfont= dict(color='black', size= 14),
                        tickcolor= 'black',
                        tickprefix= 'R$ '
                        )
        
        pontos_x = df_comparativo_geral[(df_comparativo_geral['ANO'] == years[0]) & (df_comparativo_geral['PRODUTO'] == produto)]['NM_MES'].tolist()
        
        pontos_y = df_comparativo_geral[(df_comparativo_geral['ANO'] == years[0]) & (df_comparativo_geral['PRODUTO'] == produto)]['VL_MEDIO_VENDA']
        
    
        for x, y in zip(pontos_x, pontos_y):
                            
            comp_graph.add_annotation(
                text= "R$ {}".format(y),
                x= x,
                y= float(y),
                showarrow= False,
                arrowhead=0,
                font= dict(
                    size= 12.5,
                    color= 'white'
                ),
                xref= 'x',
                yref= 'y',
                bgcolor= colors_comp[0],
                bordercolor= colors_comp[0],
                borderwidth= 2
            )

        # 2023
        comp_graph.add_trace(
            go.Scatter(
                x= df_comparativo_geral[(df_comparativo_geral['ANO'] == years[1]) & (df_comparativo_geral['PRODUTO'] == produto)]['NM_MES'],
                y= df_comparativo_geral[(df_comparativo_geral['ANO'] == years[1]) & (df_comparativo_geral['PRODUTO'] == produto)]['VL_MEDIO_VENDA'],
                marker_color= colors_comp[1],
                hovertext = "R$ " + df_comparativo_geral[(df_comparativo_geral['ANO'] == years[1]) & (df_comparativo_geral['PRODUTO'] == produto)]['VL_MEDIO_VENDA'].apply(lambda x: str(x)),
                hoverinfo= 'text',
                mode= mode,
                name = '{}'.format(years[1])
            )
        )
        
        pontos_x = df_comparativo_geral[(df_comparativo_geral['ANO'] == years[1]) & (df_comparativo_geral['PRODUTO'] == produto)]['NM_MES'].tolist()
        
        pontos_y = df_comparativo_geral[(df_comparativo_geral['ANO'] == years[1]) & (df_comparativo_geral['PRODUTO'] == produto)]['VL_MEDIO_VENDA']
        
    
        for x, y in zip(pontos_x, pontos_y):
                            
            comp_graph.add_annotation(
                text= "R$ {}".format(y),
                x= x,
                y= float(y),
                showarrow= False,
                arrowhead=0,
                font= dict(
                    size= 12.5,
                    color= 'black'
                ),
                xref= 'x',
                yref= 'y',
                bgcolor= colors_comp[1],
                bordercolor= colors_comp[1],
                borderwidth= 2
            )
        
        # Plotando
        st.plotly_chart(comp_graph, use_container_width= True)

    # Condição estado selecionado e city todos
    elif state_select != 'TODOS' and city_select == None:

        # 2022
        comp_graph = go.Figure()
        
        comp_graph.add_trace(
            go.Scatter(
                x= df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[0]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['NM_MES'],
                y= df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[0]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['VL_MEDIO_VENDA'],
                marker_color= colors_comp[0],
                hovertext = "R$ " + df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[0]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['VL_MEDIO_VENDA'].apply(lambda x: str(x)),
                hoverinfo= 'text',
                mode= mode,
                name = '{}'.format(years[0])
            )
        )
        
        comp_graph.update_layout(
        barmode= 'group',
        template= 'simple_white',
        legend= dict(
            orientation= 'h',
            font= dict(size= 15),
            x= 0.425,
            y= 1.4),
        height= 525,
        hoverlabel= dict(
            font= dict(color= 'white',
                        size= 14),
            bgcolor= 'black')
    )

        comp_graph.update_xaxes(tickfont=dict(color='black', size= 14),
                        tickcolor= 'black'
                        #tickangle= -10
                        )

        comp_graph.update_yaxes(tickfont= dict(color='black', size= 14),
                        tickcolor= 'black',
                        tickprefix= 'R$ '
                        )
        
        pontos_x = df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[0]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['NM_MES'].tolist()
        
        pontos_y = df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[0]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['VL_MEDIO_VENDA'].tolist()
        
    
        for x, y in zip(pontos_x, pontos_y):
                            
            comp_graph.add_annotation(
                text= "R$ {}".format(y),
                x= x,
                y= float(y),
                showarrow= False,
                arrowhead=0,
                font= dict(
                    size= 12.5,
                    color= 'white'
                ),
                xref= 'x',
                yref= 'y',
                bgcolor= colors_comp[0],
                bordercolor= colors_comp[0],
                borderwidth= 2
            )

        # 2023        
        comp_graph.add_trace(
            go.Scatter(
                x= df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[1]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['NM_MES'],
                y= df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[1]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['VL_MEDIO_VENDA'],
                marker_color= colors_comp[1],
                hovertext = "R$ " + df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[1]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['VL_MEDIO_VENDA'].apply(lambda x: str(x)),
                hoverinfo= 'text',
                mode= mode,
                name = '{}'.format(years[1])
            )
        )
        
        pontos_x = df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[1]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['NM_MES'].tolist()
        
        pontos_y = df_comparativo_states[
                    (df_comparativo_states['ANO'] == years[1]) & (df_comparativo_states['PRODUTO'] == produto) & (df_comparativo_states['NM_ESTADO'] == state_select)
                    ]['VL_MEDIO_VENDA'].tolist()
        
    
        for x, y in zip(pontos_x, pontos_y):
                            
            comp_graph.add_annotation(
                text= "R$ {}".format(y),
                x= x,
                y= float(y),
                showarrow= False,
                arrowhead=0,
                font= dict(
                    size= 12.5,
                    color= 'white'
                ),
                xref= 'x',
                yref= 'y',
                bgcolor= colors_comp[1],
                bordercolor= colors_comp[1],
                borderwidth= 2
            )

        
        # Plotando
        st.plotly_chart(comp_graph, use_container_width= True)

    # Condição estado selecionado e city selecionado
    elif state_select != 'TODOS' and city_select != None:

        # 2022
        comp_graph = go.Figure()
        
        comp_graph.add_trace(
            go.Scatter(
                x= df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[0]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['NM_MES'],
                y= df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[0]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['VL_MEDIO_VENDA'],
                marker_color= colors_comp[0],
                hovertext= "R$ " + df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[0]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['VL_MEDIO_VENDA'].apply(lambda x: str(x)),
                hoverinfo= 'text',
                mode= mode,
                name = '{}'.format(years[0])
                
            )
        )

        # Layout
        comp_graph.update_layout(
        barmode= 'group',
        template= 'simple_white',
        legend= dict(
            orientation= 'h',
            font= dict(size= 15),
            x= 0.425,
            y= 1.4),
        height= 525,
        hoverlabel= dict(
            font= dict(color= 'white',
                        size= 14),
            bgcolor= 'SteelBlue')
    )

        # Axes
        comp_graph.update_xaxes(tickfont=dict(color='black', size= 14),
                        tickcolor= 'black'
                        #tickangle= -10
                        )

        comp_graph.update_yaxes(tickfont= dict(color='black', size= 14),
                        tickcolor= 'black',
                        tickprefix= 'R$ '
                        )
        
        # annotations
        pontos_x = df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[0]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['NM_MES'].tolist()
        
        pontos_y = df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[0]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['VL_MEDIO_VENDA'].tolist()
        
    
        for x, y in zip(pontos_x, pontos_y):
                            
            comp_graph.add_annotation(
                text= "R$ {}".format(y),
                x= x,
                y= float(y),
                showarrow= False,
                arrowhead=0,
                font= dict(
                    size= 12.5,
                    color= 'white'
                ),
                xref= 'x',
                yref= 'y',
                bgcolor= colors_comp[0],
                bordercolor= colors_comp[0],
                borderwidth= 2
            )

        # 2023        
        comp_graph.add_trace(
            go.Scatter(
                x= df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[1]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['NM_MES'],
                y= df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[1]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['VL_MEDIO_VENDA'],
                marker_color= colors_comp[1],
                hovertext= "R$ " + df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[1]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['VL_MEDIO_VENDA'].apply(lambda x: str(x)),
                hoverinfo= 'text',
                mode= mode,
                name = '{}'.format(years[1])
                
            )
        )
        
        pontos_x = df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[1]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['NM_MES'].tolist()
        
        pontos_y = df_comparativo_citys[
                    (df_comparativo_citys['ANO'] == years[1]) & (df_comparativo_citys['PRODUTO'] == produto) & (df_comparativo_citys['NM_ESTADO'] == state_select) & (df_comparativo_citys['MUNICIPIO'] == city_select)
                    ]['VL_MEDIO_VENDA'].tolist()
        
    
        for x, y in zip(pontos_x, pontos_y):
                            
            comp_graph.add_annotation(
                text= "R$ {}".format(y),
                x= x,
                y= float(y),
                showarrow= False,
                arrowhead=0,
                font= dict(
                    size= 12.5,
                    color= 'white'
                ),
                xref= 'x',
                yref= 'y',
                bgcolor= colors_comp[1],
                bordercolor= colors_comp[1],
                borderwidth= 2
            )
                
        # Plotando
        st.plotly_chart(comp_graph, use_container_width= True)

# Line 1
# Titulo + line_1
st.markdown("<h1 style='text-align: center; color: black;'>Preço dos combustíveis no Brasil 💵⛽<br> {}</h1>".format(produto), unsafe_allow_html=True)
st.divider()
line_1()
st.divider()

# Titulo + line_2
st.markdown("<h3 style='text-align: center; color: black;'>Valor médio por estado</h3>", unsafe_allow_html=True)
st.divider()
line_2()
st.divider()

# Titulo + line_3
st.markdown("<h3 style='text-align: center; color: black;'>Comparativo Anual - Valor médio por mês</h3>", unsafe_allow_html=True)
line_3()
st.divider()

