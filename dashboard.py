import pandas as pd
import inflection
import streamlit as st
import plotly.express as px
from PIL import Image 

# functions
def get_data(path):
    data = pd.read_csv(path)
    return data 

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

def dict_to_df(dicto, col1, col2):
    df = pd.DataFrame.from_dict(dicto, orient='index')
    df = df.reset_index()
    df.rename(columns = {'index':col1, 0: col2}, inplace=True)
    return df

def transform(data, countries, colors, fx):
    ## Removendo Outlier da Austrália
    cond1 = (data['country_code'] == 14)
    cond2 = (data['average_cost_for_two'] == 25000017)
    data.loc[cond1 & cond2, :] ## Verificando e confirmando de que é só australia
    data = data[data['average_cost_for_two'] != 25000017] # removendo da Base
    # Removendo NAN
    data = data.loc[pd.isna(data['cuisines']) != True, :]
    # Deixando Cuisines Unicos 
    data['cuisines'] = data.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
    # Removendo Duplicatas
    df = data.drop_duplicates(subset=['restaurant_id'])
    df = df.reset_index(drop=True)
    # Fazendo Merge com os dfs, colors, countries, fx e iso
    df1 = df.merge(countries, how='left', left_on='country_code', right_on='id')
    df1 = df1.merge(colors, how='left', left_on='rating_color', right_on='id')
    df1 = df1.merge(fx, how='left', left_on='currency', right_on='id')
    df1 = df1.merge(iso, how='left', left_on='country', right_on='country')
    ### Converter Valores Para USD
    df1['average_cost_for_two_usd'] = df1['average_cost_for_two'] * df1['price']
    # reset de index
    df1 = df1.reset_index(drop=True)
    # Removendo colunas
    df1 = df1.drop(['country_code', 'id_x', 'id_y', 'id', 'price'], axis = 1)
    return df1

def price_range(price):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

# Extraction
data = get_data('zomato.csv')

COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

FX = {
    'Botswana Pula(P)': 0.076,
    'Brazilian Real(R$)': 0.19,
    'Dollar($)': 1,
    'Emirati Diram(AED)': 0.27,
    'Indian Rupees(Rs.)': 0.012,
    'Indonesian Rupiah(IDR)': 0.000064,
    'NewZealand($)': 0.64,
    'Pounds(£)': 1.21,
    'Qatari Rial(QR)': 0.27,
    'Rand(R)': 0.057,
    'Sri Lankan Rupee(LKR)': 0.027,
    'Turkish Lira(TL)': 0.054
}

ISO_COUNTRIES = {
    'Philippines': 'PHL',
    'Brazil': 'BRA',
    'Australia':'AUS',
    'United States of America':'USA',
    'Canada':'CAN',
    'Singapure': 'SGP',
    'United Arab Emirates': 'ARE',
    'India': 'IND',
    'New Zeland': 'NZL',
    'England': 'GBR',
    'Qatar': 'QAT',
    'South Africa': 'ZAF',
    'Sri Lanka': 'LKA',
    'Turkey' : 'TUR'} 

## Transform 
colors = dict_to_df(COLORS, 'id', 'color')
countries = dict_to_df(COUNTRIES, 'id', 'country')
fx = dict_to_df(FX, 'id', 'price')
iso = dict_to_df(ISO_COUNTRIES, 'country', 'iso')
data = rename_columns(data)
data_raw = transform(data, countries, colors, fx)

### ================================================ 
### Geral                                            
### ================================================ 
st.header('Market Place Deu Fome - KPIs') #Escrever cabeçalho 
### ================================================ 
### Barra lateral                                      
### ================================================ 
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=300)
### Sidebar
st.sidebar.markdown('# Deu Fome')
st.sidebar.markdown('## O Marketplace de Comida')
st.sidebar.markdown("""---""")
countries = data_raw['country'].unique()
side_select = st.sidebar.multiselect('Selecione um País', countries, default= ['England', 'India', 'Singapure'])
min_prince = int(data_raw['average_cost_for_two_usd'].min())
max_prince = int(data_raw['average_cost_for_two_usd'].max())
slider_select = st.sidebar.slider('Preço', min_prince, max_prince, max_prince )
st.sidebar.markdown('Powered By Jesus Teixeira')
### Filtros na Base
linhas_selecionadas1 = data_raw['average_cost_for_two_usd'] <= slider_select
linhas_selecionadas2 = data_raw['country'].isin(side_select)
data_raw = data_raw.loc[linhas_selecionadas1, :]
data_raw = data_raw.loc[linhas_selecionadas2, :]
### ================================================ 
### layout da Página                                     
### ================================================ 

tab1, tab2, tab3, tab4 = st.tabs(['Geral','Países', 'Cidades', 'Culinária'])

## Visão Geral 
with tab1: 
    # 1.Quantos restaurantes únicos estão registrados?
    qtd_restaurante = len(data_raw['restaurant_id'].unique())
    # 2.Quantos países únicos estão registrados?
    qts_countries = len(data_raw['country'].unique())
    # 3.Quantas cidades únicas estão registradas?
    qtd_city = len(data_raw['city'].unique())
    # 4.Qual o total de avaliações feitas?
    total_votes = data_raw['votes'].sum()
    # 5.Qual o total de tipos de culinária registrados?
    a = data['cuisines'].apply(lambda x : str(x).split(',')[0])  ## Criando listas em cada llinha e atribuindo a uma variavel
    all_cuisines = [j.strip() for i in a for j in i] ## Transformando tudo numa lista só
    total_cuisines = len(set(all_cuisines))
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Total de Restaurantes", value=qtd_restaurante)
    with col2:
        st.metric(label="Países",  value=qts_countries)
    with col3:  
        st.metric(label="Cidades", value=qtd_city)
    with col4:
        st.metric(label="Número de Pedidos", value=total_votes)
    with col5:
        st.metric(label = 'Variedade de Culinárias', value= total_cuisines)
    ### Mapa
    to_map = data_raw[['country', 'iso','average_cost_for_two_usd']].groupby(['country', 'iso']).mean().reset_index()
    fig = px.choropleth(to_map, locations='iso' , color='average_cost_for_two_usd',
                        hover_name='country', title='Custo máximo de uma refeição para dois (USD)' ,range_color=[10,150])
    st.plotly_chart(fig, use_container_width=True)
    ### pie chart 1 
    ax = data_raw[['has_table_booking', 'restaurant_id']].groupby('has_table_booking').count().reset_index()
    ax['has_table_booking'] = ax['has_table_booking'].apply(lambda x:'Não' if x == 0 
                                                            else 'Sim')
    fig1 = px.pie(ax, values='restaurant_id', names='has_table_booking', title='Restaurantes que Aceitam Reserva')
    st.plotly_chart(fig1, use_container_width=True)
    ## pie chart 2
    ax1 = data_raw[['has_online_delivery', 'restaurant_id']].groupby('has_online_delivery').count().reset_index()
    ax1['has_online_delivery'] = ax1['has_online_delivery'].apply(lambda x:'Não' if x == 0 
                                                            else 'Sim')
    fig2 = px.pie(ax1, values='restaurant_id', names='has_online_delivery', title='Restaurantes que tem Delivery')
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown('## Visão dos Países')
    ## Quantidade de Cidades por País
    pa1 = data_raw[['country', 'city']].groupby('country').nunique().reset_index()
    pa1 = pa1.sort_values('city', ascending = False).reset_index(drop=True)  
    fig3 = px.bar(pa1, x='city', y='country', title = 'Quantidade de Cidades por País', labels={'city': 'Cidades', 'country': ""} )
    st.plotly_chart(fig3, use_container_width=True)
    ## Top 5 países mais caros
    pa11 = data_raw[['country', 'average_cost_for_two_usd']].groupby('country').mean().reset_index().sort_values('average_cost_for_two_usd', ascending = False)
    pa11 = pa11.iloc[0:5, :]
    fig4 = px.bar(pa11, x='country', y='average_cost_for_two_usd', title='Top 5 Países mais caros (USD)', labels={'country': 'País', 'average_cost_for_two_usd': "Custo médio"})
    st.plotly_chart(fig4, use_container_width=True)
    ## Nota Média por País 
    pa9 = data_raw[['country', 'aggregate_rating']].groupby('country').mean().reset_index().sort_values('aggregate_rating', ascending = False).reset_index(drop=True)
    pa9.rename(columns={'country': "País", 'aggregate_rating' : 'Nota Média'}, inplace = True)
    st.markdown('Nota Média por País')
    st.dataframe(pa9)

with tab3:
    # Top 10 Cidades com mais Restaurantes
    c1 = data_raw[['city', 'restaurant_id']].groupby('city').count().reset_index().sort_values('restaurant_id', ascending = False)
    c1 = c1.iloc[0:10, :]
    fig5 = px.bar(c1, x= 'city', y='restaurant_id', title = 'Top cidades com mais restaurantes', labels={'restaurant_id': 'quantidade de restaurantes', 'city':'cidades'})
    st.plotly_chart(fig5, use_container_width=True)
    ## Top 5 cidades mais caros
    c11 = data_raw[['city', 'average_cost_for_two_usd']].groupby('city').mean().reset_index().sort_values('average_cost_for_two_usd', ascending = False)
    c11 = c11.iloc[0:5, :]
    fig6 = px.bar(c11, x='city', y='average_cost_for_two_usd', title='Top 5 Cidades mais caros (USD)', labels={'city': 'País', 'average_cost_for_two_usd': "Custo médio"})
    st.plotly_chart(fig6, use_container_width=True)
    # Nota Média por Cidade
    c9 = data_raw[['city', 'aggregate_rating']].groupby('city').mean().reset_index().sort_values('aggregate_rating', ascending = False).reset_index(drop=True)
    c9 = c9.iloc[0:10, :]
    fig7 = px.bar(c9, x = 'city', y = 'aggregate_rating', title='Melhores notas por cidade')
    st.plotly_chart(fig7, use_container_width=True)
    #Qual o nome da cidade que possui a maior quantidade de restaurantes que fazem entregas?
    c7 = data_raw.loc[data_raw['is_delivering_now'] == 1, :][['city', 'restaurant_id']].groupby('city').count().reset_index().sort_values('restaurant_id', ascending = False)
    c7 = c7.iloc[0:10, :]
    st.markdown('Cidades com mais restaurantes que fazem delivery')
    st.dataframe(c7)

with tab4: 
    # TOP culinarias mais caras
    c11 = data_raw[['cuisines','average_cost_for_two_usd']].groupby('cuisines').mean().sort_values('average_cost_for_two_usd', ascending = False).reset_index()
    c11 = c11.iloc[0:10, :]
    fig8 = px.bar(c11, x = 'cuisines', y = 'average_cost_for_two_usd', title='Preço médio por tipo de culunária')
    st.plotly_chart(fig8, use_container_width=True)
    # Top nmotas por cuisines 
    c12 = data_raw[['cuisines','aggregate_rating']].groupby('cuisines').mean().sort_values('aggregate_rating', ascending = False).reset_index()
    c12 = c12.iloc[0:10, :]
    fig9 = px.bar(c12, x = 'cuisines', y = 'aggregate_rating', title='Melhor avaliação média por culinária')
    st.plotly_chart(fig9, use_container_width=True)
