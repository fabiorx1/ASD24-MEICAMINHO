import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import cempre, ibge
import locale, warnings

warnings.filterwarnings("ignore")
cempre.initialize(['MG', 'SP', 'RJ'])
ufs = cempre.get_ufs()
divisoes = cempre.get_divisoes()
brl = lambda v: locale.currency(v, grouping=True, symbol='R$')
brn = lambda v: locale.format_string('%d', v, grouping=True)

st.write(str(locale.locale_alias))
st.write(
    """
    # Olá, empreendedor!
    ## E ai, tá MEI perdido?
    Com as informações certas, você já tem **MEI caminho andado!**
    
    Faça análises de mercado e se informe em **poucos cliques**!
    
    """)

with st.container(border=True):
  st.write("## Região")
  estado = st.selectbox("Selecione seu estado:", ufs)
  if estado:
    df = cempre.get_dataframe_by_uf(estado)
    cidades = df[df.columns[0]].unique()
    cidade = st.selectbox("Selecione sua cidade:", cidades)
    if cidade: df = df[df[df.columns[0]] == cidade]

with st.container(border=True):
  st.write("## Setor")
  setor = st.selectbox("Selecione seu setor:", divisoes)
  if setor:
    cnaes = cempre.get_cnaes(setor).values
    cnae = st.selectbox("Selecione sua atividade:", cnaes)
    if cidade and cnae:
      line = df[df[df.columns[2]] == cnae].reset_index(drop=True)
      salario_medio = line[line.columns[-1]][0]
      n_empresas = line[line.columns[3]][0]
      n_pessoas = line[line.columns[6]][0]
      media_pessoas_empresa = (n_pessoas/n_empresas) if n_empresas else 0
      populacao = ibge.get_populacao(cidade)

if cnae and cidade:
  with st.container(border=True):
    st.write("## O que já sabemos:")
    with st.container(border=True):
      st.write("### População")
      st.write(f"- {cidade.split(' - ')[0]} possui uma população estimada de **{brn(populacao)} habitantes**.")
      st.write(f'- Existem **{n_empresas} empresas** que atuam na atividade **"{cnae}"**.')
      st.write(f'- **{int(n_pessoas)} pessoas** estão empregadas na atividade **"{cnae}"**.')
    with st.container(border=True):
      st.write("### Salários e funcionários")
      st.write(f"- O salário médio para a atividade é de **{brl(salario_medio)}/mês***")
      st.write("- São aproximadamente **%.2f pessoas por empresa***" % media_pessoas_empresa)
      with st.container(border=True):
        st.write(
          f"""
          Isso significa que manter uma empresa nesse setor **custa**, em média:
          - ##### {brl(media_pessoas_empresa*salario_medio)}/mês, considerando apenas os salários*.""")
    st.caption('*Dados de 2022')
  
  if 'show_charts' not in st.session_state: st.session_state.show_charts = False
  if 'mortality' not in st.session_state: st.session_state.mortality = False
  if 'learn_more' not in st.session_state: st.session_state.learn_more = False
  
  def show_charts():
    st.session_state.show_charts = True
    st.session_state.mortality = False
    st.session_state.learn_more = False
  st.button('Gráficos comparativos entre setores', icon='📊', on_click=show_charts)
  
  def show_mortality():
    st.session_state.mortality = True
    st.session_state.show_charts = False
    st.session_state.learn_more = False
  st.button('Tendências das empresas', icon='⭐', on_click=show_mortality)
  
  def learn_more():
    st.session_state.learn_more = True
    st.session_state.mortality = False
    st.session_state.show_charts = False
  st.button('Aprender mais +', icon='📚', on_click=learn_more)
      
  if st.session_state.mortality:
    with st.container(border=True):
      st.write('### Tendências')
      st.divider()
      st.write('#### Brasil')
      ge_br_abs, ge_br, gp_br_abs, gp_br = cempre.get_tendencia(setor, 'Brasil')
      cols = st.columns(2)
      with cols[0]:
        with st.container(border=True):
          st.write(f'No Brasil, o número de **empresas** no setor de *{setor}* '
                   + ('**aumentou' if ge_br>0 else '**diminuiu')
                   + ' %.2f%%** em 2021.' %  ge_br)
          st.write(f'O número de **funcionários** no setor de *{setor}* '
                   + ('**aumentou' if gp_br>0 else '**diminuiu')
                   + ' %.2f%%** em 2021.' %  gp_br)
      with cols[1]:
        with st.container(border=True): st.write(f'Isso corresponde a **{brn(ge_br_abs)} empresas**.')
        with st.container(border=True): st.write(f'Isso corresponde a **{brn(gp_br_abs)} pessoas**.')
  
      st.write(f'#### {ibge.nomes_estados[estado]}')
      ge_uf_abs, ge_uf, gp_uf_abs, gp_uf = cempre.get_tendencia(setor, ibge.nomes_estados[estado])
      cols = st.columns(2)
      with cols[0]:
        with st.container(border=True):
          st.write(f'Em {estado}, o número de empresas no setor de *{setor}* '
                   + ('**aumentou' if ge_uf>0 else '**diminuiu')
                   + ' %.2f%%** em 2021.' %  ge_uf)
          st.write(f'O número de **funcionários** no setor de *{setor}* '
                   + ('**aumentou' if gp_uf>0 else '**diminuiu')
                   + ' %.2f%%** em 2021.' %  gp_uf)
      with cols[1]:
        with st.container(border=True):
          st.write(f'Isso corresponde a **{brn(ge_uf_abs)} empresas**.')
        with st.container(border=True):
          st.write(f'Isso corresponde a **{brn(gp_uf_abs)} pessoas**.')
      
  
  if st.session_state.show_charts:
    with st.container(border=True):
      st.write("### Gráficos comparativos")
      macros_df = df[df[df.columns[1]].apply(lambda c: not str(c).isdigit())]
      macros_df = macros_df.drop(macros_df.index[0])
      cnaes_df = df[df[df.columns[2]].apply(lambda c: c in cnaes)]
      cols = [df.columns[j] for j in [3, 6, 8, 9]]
      col = st.selectbox("Selecione uma informação:", cols)
      if col:
        fig, ax = plt.subplots()
        ax.set_title(f'{col} por atividade do setor')
        ax.barh(cnaes, cnaes_df[col], color='lightblue')
        ax.barh(cnae, cnaes_df[cnaes_df[df.columns[2]] == cnae][col], color='midnightblue')
        ticks_y = ax.get_yticks()
        ax.set_yticks(ticks_y, [c[:23] + ('...' if len(c)>20 else '') for c in cnaes_df[df.columns[2]]])
        ax.tick_params('x', rotation=30)
        if col.endswith(' (R$) '):
          ax.set_xticks(ax.get_xticks(), [brl(tick) for tick in ax.get_xticks()])
        fig.tight_layout()
        st.pyplot(fig)
        
        fig, ax = plt.subplots()
        ax.set_title(f'{col} por setor')
        ax.barh(macros_df[df.columns[2]], macros_df[col], color='mediumpurple')
        ax.barh(setor, macros_df[macros_df[df.columns[2]] == setor][col], color='indigo')
        ticks_y = ax.get_yticks()
        ax.set_yticks(ticks_y, [c[:23] + ('...' if len(c)>20 else '') for c in macros_df[df.columns[2]]])
        ax.grid(), ax.tick_params('x', rotation=30)
        if col.endswith(' (R$) '):
          ax.set_xticks(ax.get_xticks(), [brl(tick) for tick in ax.get_xticks()])
        fig.tight_layout()
        st.pyplot(fig)
  
  if st.session_state.learn_more:
    with st.container(border=True):
      st.write("## Viabilidade de Negócios")
      st.caption('Um resumo com IA de uma cartilha do SEBRAE.')
      st.write(f"""
                ### O que é viabilidade de negócios?

                Viabilidade de negócios é a análise que permite verificar se um empreendimento é financeiramente viável, ou seja, se ele será capaz de gerar lucro e retornar o investimento inicial.

                ### Quais são as principais etapas para analisar a viabilidade de um negócio?

                - Investimentos fixos
                - Gastos fixos mensais
                - Capital de giro inicial
                - Investimento inicial total
                - Metas de venda
                - Gastos variáveis
                - Ponto de equilíbrio
                - Demonstrativo de resultados
                - Retorno do investimento

                ### O que são investimentos fixos?

                São os bens essenciais para o funcionamento da empresa, como reformas, móveis, equipamentos e computadores.

                ### O que compõe o capital de giro inicial?

                - Reserva para cobertura de gastos fixos mensais nos primeiros meses
                - Constituição da empresa
                - Marketing inicial
                - Treinamentos e certificações
                - Estoque inicial

                ### Como calcular o ponto de equilíbrio?

                O ponto de equilíbrio é calculado dividindo-se o valor dos gastos fixos mensais pela margem de contribuição percentual.

                ### O que é o demonstrativo de resultados?

                É um relatório que mostra todas as receitas e gastos da empresa, permitindo identificar se houve lucro ou prejuízo em determinado período.

                ### Como calcular o tempo de retorno do investimento?

                Divide-se o valor do investimento inicial total pelo lucro mensal estimado, somando-se a quantidade de meses em que a empresa terá prejuízo inicialmente.

                ### Por que é importante analisar a viabilidade do negócio?

                - Permite prever riscos e problemas potenciais
                - Ajuda a tomar decisões estratégicas
                - Possibilita comparar com outras opções de investimento
                - Evita endividamento e perda do capital investido

                ### Com que frequência devo analisar a viabilidade do meu negócio?

                É recomendável elaborar o demonstrativo de resultados mensalmente para acompanhar o desempenho financeiro da empresa e tomar decisões baseadas em dados atualizados.
               """)


# Button to generate chart
    # # Data for the bar chart
    # data = pd.DataFrame({
    #     "Option": [selected_option],
    #     "Value": [number_input]
    # })
    
    # # Plot the bar chart
    # fig, ax = plt.subplots()
    # ax.bar(data["Option"], data["Value"], color="blue")
    # ax.set_ylabel("Value")
    # ax.set_title("Bar Chart")
    
    # # Show the chart
    # st.pyplot(fig)