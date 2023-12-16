import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ORÇA OBRAS", page_icon=None, layout="wide")
st.title("ORÇA OBRAS 2023")
# leitura do arquivo Excel
##df = pd.read_excel('composicoes_preco_unitario.xlsx')
k = "SINAPI.xls"

@st.cache_data
def sinapi():
    global df
    # Ler o arquivo como um dataframe do Pandas
    df = pd.read_excel((k), header=5, usecols='A,G,H,N,Q', nrows=46487, converters={'CODIGO DA COMPOSICAO':str})               
    #trocar a vírgula decimal por ponto na coluna de coeficientes
    cols = ['COEFICIENTE']
    df[cols]=df[cols].replace(',','.', regex=True).astype(float)
    #df['DESCRICAO DA COMPOSICAO'].apply(lambda x: x.lower())
    df['DESCRICAO DA COMPOSICAO'] = df['DESCRICAO DA COMPOSICAO'].str.title()
    return df
df = sinapi()


# criação da lista de classes
classes = df['DESCRICAO DA CLASSE'].unique()

# sidebar com os botões radio das classes
classe_selecionada = st.sidebar.radio('Selecione a classe', classes)

# filtro do dataframe pelo valor da coluna 'classe'
df_filtrado = df[df['DESCRICAO DA CLASSE'] == classe_selecionada]

# exibição da lista de serviços
servicos = st.multiselect("Selecione o serviço", df_filtrado['DESCRICAO DA COMPOSICAO'].unique())    

# criação do novo dataframe com os serviços selecionados, se ainda não tiver sido criado
if "df_selecionado" not in st.session_state:
    st.session_state.df_selecionado = df_filtrado.loc[df_filtrado['DESCRICAO DA COMPOSICAO'].isin(servicos)]
df_selecionado = st.session_state.df_selecionado

st.header("df_selecionado inicial (ou da sessão anterior), salvo em session_state")
st.write(st.session_state.df_selecionado)

# criação do novo dataframe com os serviços selecionados
#df_selecionado = df_filtrado.loc[df_filtrado['DESCRICAO DA COMPOSICAO'].isin(servicos)]

##st.write(df_selecionado)

# criar um dicionário para armazenar os serviços selecionados e suas quantidades
servicos_quantidades = {}

# percorrer a lista de serviços selecionados e solicitar a quantidade desejada para cada um
count = 0
for servico in servicos:
    count += 1
    quantidade = st.number_input(f"Quantidade desejada para {servico}", key=count)
    servicos_quantidades[servico] = quantidade

##st.write(servicos_quantidades)

# filtrar o dataframe para conter apenas as linhas que correspondem aos serviços selecionados
df_selecionado = df.query("`DESCRICAO DA COMPOSICAO` in @servicos") #precisa ser com crase

##st.write(df_selecionado.columns)
##st.write(len(df_selecionado))

# adicionar coluna 'qtde_desejada'
df_selecionado['qtde_desejada'] = 0

if len(df_selecionado) >0:    
    # calcular a quantidade desejada de cada insumo e armazenar em uma nova coluna
    df_selecionado['qtde_desejada'] = df_selecionado.apply(lambda row: row['COEFICIENTE'] * servicos_quantidades[row['DESCRICAO DA COMPOSICAO']], axis=1)

#==ERRO==
##st.write(df_selecionado)

# criar um novo dataframe contendo apenas as colunas desejadas e exibi-lo para o usuário
#df_insumos = df_selecionado[['DESCRICAO DA COMPOSICAO', 'DESCRIÇÃO ITEM', 'qtde_desejada']]

# multiplicação pelo valor 'per_capita' de cada insumo
df_selecionado['total'] = df_selecionado['COEFICIENTE'] * df_selecionado['qtde_desejada']

#apresenta o detalhamento por serviço
st.header("DETALHAMENTO DOS SERVIÇOS SELECIONADOS")
df_selecionadox = df_selecionado.loc[:, ["DESCRICAO DA COMPOSICAO", "DESCRIÇÃO ITEM", "qtde_desejada"]]
st.header("df_selecionadox atual, após calcular o total, e só com as colunas desejadas")
st.write(df_selecionadox)



st.header("session_state atual, após criado o novo df_selecionado")
st.write(st.session_state.df_selecionado)

st.header("df_selecionado atual")
st.write(df_selecionado)

# Botão para salvar tabela
if st.button('Salvar tabela'):
    ##a união do df que está em session_state.df_selecionado com object
    ##df_selecionado atual não está funcionando
    
    st.session_state.df_selecionado = pd.concat([ st.session_state.df_selecionado , df_selecionado ], axis=0)
    z = st.session_state.df_selecionado
    
    
    
    #st.session_state.df_selecionado = df_selecionado
    st.write('Tabela salva com sucesso!')
    
# Botão para exportar tabela
if st.button('Exportar'):
    df_selecionado = st.session_state.df_selecionado
    
    #agora somando os insumos de todos os serviços
    df_agrupado = z.groupby(['DESCRIÇÃO ITEM'])['qtde_desejada'].sum().reset_index(name='qtde_total')
    df_agrupado = df_agrupado.loc[:, ["DESCRIÇÃO ITEM", "qtde_total"]]
    #st.write(df_agrupado)
    
    #nome_arquivo = classe_selecionada + '.xlsx'
    with pd.ExcelWriter('saida.xlsx') as writer:
        df_selecionado.to_excel(writer, sheet_name='Selecionados')
        df_agrupado.to_excel(writer, sheet_name='Agrupados')

    # Salve o arquivo Excel
    writer.save()
    st.write('Tabela exportada com sucesso!')
    

