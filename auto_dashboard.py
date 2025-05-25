# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

st.set_page_config(layout="wide")
st.title("📊 Dashboard Avançado com Filtros e Exportação")

arquivo = st.file_uploader("📁 Selecione um arquivo Excel (.xlsx)", type=["xlsx"])

def exportar_pdf(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Relatório - Tabela Tratada", ln=True, align="C")
    pdf.ln(10)

    for i in range(len(df)):
        row = ', '.join([str(x) for x in df.iloc[i]])
        pdf.multi_cell(0, 8, txt=row)

    output = io.BytesIO()
    pdf.output(output)
    st.download_button("📥 Baixar PDF da Tabela", data=output.getvalue(), file_name="relatorio_dashboard.pdf")

if arquivo:
    try:
        df = pd.read_excel(arquivo)

        st.subheader("📋 Dados Originais")
        st.dataframe(df.head())

        df = df.dropna(how='all').dropna(axis=1, how='all').drop_duplicates().fillna(0)
        df.columns = [col.strip().title() for col in df.columns]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')

        nome_saida = "tabela_tratada.xlsx"
        df.to_excel(nome_saida, index=False)
        st.success(f"Tabela tratada salva como: {nome_saida}")

        col_numericas = df.select_dtypes(include='number').columns.tolist()
        col_categoricas = df.select_dtypes(exclude='number').columns.tolist()

        if not col_numericas:
            df['Contagem'] = 1
            col_numericas = ['Contagem']

        st.subheader("🎯 Filtros Interativos")
        filtro_categoria = None
        if col_categoricas:
            col_filtro = st.selectbox("Filtrar por categoria:", col_categoricas)
            opcoes = df[col_filtro].unique().tolist()
            filtro_categoria = st.multiselect(f"Escolha os valores de {col_filtro}", opcoes, default=opcoes)
            df = df[df[col_filtro].isin(filtro_categoria)]

        if col_numericas and col_categoricas:
            col_cat = st.selectbox("📌 Coluna categórica:", col_categoricas)
            col_valor = st.selectbox("📊 Coluna numérica:", col_numericas)

            st.markdown("### 📈 Gráficos Interativos")

            col1, col2 = st.columns(2)

            with col1:
                fig_barra = px.bar(df, x=col_cat, y=col_valor, color=col_cat, title="Gráfico de Barras")
                st.plotly_chart(fig_barra, use_container_width=True)

                fig_pizza = px.pie(df, names=col_cat, values=col_valor, title="Gráfico de Pizza")
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col2:
                fig_hist = px.histogram(df, x=col_valor, title="Histograma")
                st.plotly_chart(fig_hist, use_container_width=True)

                col_data = None
                for c in df.columns:
                    if "data" in c.lower():
                        col_data = c
                        break

                if col_data:
                    try:
                        df[col_data] = pd.to_datetime(df[col_data])
                        df = df.sort_values(by=col_data)
                        fig_linha = px.line(df, x=col_data, y=col_valor, color=col_cat,
                                            title="Gráfico de Linha Temporal")
                        st.plotly_chart(fig_linha, use_container_width=True)
                    except:
                        st.warning(f"Coluna '{col_data}' não pôde ser convertida para data.")

            st.subheader("📄 Tabela Final Filtrada")
            st.dataframe(df)

            st.download_button("📥 Baixar Excel Tratado", data=df.to_excel(index=False), file_name="tabela_filtrada.xlsx")

            exportar_pdf(df)
        else:
            st.warning("A tabela precisa ter pelo menos uma coluna categórica e uma numérica.")
    except Exception as e:
        st.error(f"Erro ao processar: {e}")
