# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 11:25:24 2021

@author: Pipe San Martín
"""


import re
import string
import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st





#@st.cache
def clean_text(text):
    

    clean = re.sub(r"""
                   [,;@#?!&$()]+  
                   \ * 
                   """,
                   " ",
                   text, flags=re.VERBOSE)
    
    tmp_monto = clean.split()[0]
    
    if "-" in tmp_monto:
        
        monto = 0 - int(tmp_monto.translate(str.maketrans('', '', string.punctuation)))
        
    else:
        
        monto = int(tmp_monto.translate(str.maketrans('', '', string.punctuation)))

    fecha = clean.split()[-1]
    tmp_descripcion = clean.split()[1:-1]
    str_tmp_description = " ".join(tmp_descripcion)
    
    if ":" in str_tmp_description:

        tipo = str_tmp_description.split(":")[0]
        str_description = str_tmp_description.split(":")[1]

    
    else:
        
        tipo = tmp_descripcion[0]
        str_description = " ".join(tmp_descripcion[1:])
    
    return monto, fecha, tipo, str_description

#@st.cache(suppress_st_warning=True)
def crea_dataframe(movimientos):
    
    montos = []
    fechas = []
    tipos = []
    destinos = []

    for move in movimientos:

        tmp_m, tmp_f, tmp_t, tmp_d = clean_text(move)

        montos.append(tmp_m)
        fechas.append(tmp_f)
        tipos.append(tmp_t)
        destinos.append(tmp_d)
    
    tmp_dic = {
        "Monto": montos,
        "Tipo": tipos,
        "Destino": destinos,
        "Fecha": fechas
    }
    
    dataframe = pd.DataFrame(tmp_dic)
    
    return dataframe


#@st.cache
def new_features(df, monto="Monto", fecha="Fecha", destino="Destino"):
    
    df['Direction'] = np.where(df[monto] > 0, "IN", "OUT")
    df[fecha] = pd.to_datetime(df[fecha], format='%m/%d/%y')
    df['Mes'] = [i.month for i in df[fecha]]
    df['Año'] = [i.year for i in df[fecha]]
    df['Dia de la semana'] = df[fecha].apply(lambda x: dt.datetime.strftime(x, '%A'))
    df['Dia del año'] = [i.dayofyear for i in df[fecha]]
    df['Dia del mes'] = [i.day for i in df[fecha]]
    df['Description_monto'] = df[monto].astype(str).str.cat(df[destino], sep=': ')
    
    return df

@st.cache
def convierte_fecha_en_indice(df, col='Fecha'):
        
    df[col] = pd.to_datetime(df[col])
    df = df.set_index(col)
    df = df.sort_index()
        
    return df

@st.cache
def transaction_group(df, monto_actual):
    
    transactions_date_group = df.groupby('Fecha').agg({
    'Description_monto': ', '.join,
    'Monto':'sum'
    })
    
    todo = transactions_date_group['Monto'].sum()
    final = monto_actual
    inicio = final - todo
    
    transactions_date_group['Running balance'] = inicio + transactions_date_group['Monto'].cumsum()
    
    
    daily_index = pd.date_range(transactions_date_group.index.min(),
                            transactions_date_group.index.max())

    df_daily = pd.DataFrame(transactions_date_group['Running balance'])
    df_daily = df_daily.reindex(daily_index, fill_value=np.nan)
    df_daily = df_daily.fillna(method='ffill')
    df_monthly = pd.DataFrame(df_daily['Running balance'].resample(rule='1M').mean())
    
    return transactions_date_group, df_daily, df_monthly

#@st.cache
def ingresos_group(df):
    
    ingresos_df = df[df['Direction'] == 'IN']

    ingresos_date_group = ingresos_df.groupby('Fecha').agg({
        'Tipo': ', '.join,
        'Monto':'sum'
    })
    
    ingresos_monthly = pd.DataFrame(ingresos_date_group['Monto'].resample(rule='1M').sum())
    
    return ingresos_df, ingresos_monthly

#@st.cache
def gastos_group(df):
    
    gastos_df = df[df['Direction'] == 'OUT']

    gastos_df['Monto'] = gastos_df['Monto'].apply(lambda x: 0 - x)
    
    gastos_date_group = gastos_df.groupby('Fecha').agg({
        'Tipo': ', '.join,
        'Monto':'sum'
    })
    
    gastos_monthly = pd.DataFrame(gastos_date_group['Monto'].resample(rule='1M').sum())
    
    return gastos_df, gastos_monthly

@st.cache
def crea_dff_in_out(df):
    
    dff = convierte_fecha_en_indice(df, col='Fecha')
    dff = dff.groupby(["Fecha", "Destino"]).agg({
        'Monto':'sum'
    }).reset_index()
    
    dff['Direction'] = np.where(dff['Monto'] > 0, 'In', 'Out')
    dff['Monto'] = np.where(dff['Monto'] > 0, dff['Monto'], 0-dff['Monto'])
    dff = convierte_fecha_en_indice(dff, col='Fecha')
    in_dff = dff[dff['Direction'] == "In"]
    out_dff = dff[dff['Direction'] == "Out"]
    
    return dff, in_dff, out_dff

@st.cache
def prepara_para_bar_race(df, valor="Monto", columna="Destino", agrupa_por="1M"):
    
    indice = df.index
    data_tmp = df.pivot_table(values=valor, index=indice, columns=columna, aggfunc='first')
    data_tmp_agrupado = pd.DataFrame(data_tmp.resample(rule=agrupa_por).sum())
    columnas = data_tmp_agrupado.columns.tolist()
    data_tmp_agrupado[columnas] = data_tmp_agrupado[columnas].applymap(np.int64)
    data_tmp_agrupado_cum = data_tmp_agrupado.cumsum(axis=0)
    
    return data_tmp_agrupado, data_tmp_agrupado_cum

@st.cache
def prepara_para_sankey(ingresos, gastos):
    
    ingresos['Tipo'] = ingresos['Tipo'].str.replace('Pago','Pago de')
    
    ingresos_grouped = ingresos.groupby(["Tipo", "Destino"]).agg({
    'Monto':'sum'
    }).reset_index()
    ingresos_grouped = ingresos_grouped.sort_values(['Monto'], ascending=False).head(10).reset_index(drop=True)
    ingresos_grouped['Fuente'] = ingresos_grouped['Destino']
    ingresos_grouped['Destino'] = ingresos_grouped['Tipo']
    ingresos_grouped = ingresos_grouped.loc[:,['Fuente', 'Destino', 'Monto']]
    
    gastos_grouped = gastos.groupby(["Tipo", "Destino"]).agg({
    'Monto':'sum'
    }).reset_index()
    gastos_grouped = gastos_grouped.sort_values(['Monto'], ascending=False).head(10).reset_index(drop=True)
    gastos_grouped.columns = ['Fuente', 'Destino', 'Monto']
    
    
    
    ingresos_tipo = ingresos.groupby(["Tipo"]).agg({
    'Monto':'sum'
    }).reset_index()
    ingresos_tipo['Destino'] = 'Yo'
    ingresos_tipo.columns = ['Fuente', 'Monto', 'Destino']
    
    gastos_tipo = gastos.groupby(["Tipo"]).agg({
    'Monto':'sum'
    }).reset_index()
    gastos_tipo['Fuente'] = "Yo"
    gastos_tipo.columns = ['Destino', 'Monto', 'Fuente']
    gastos_tipo = gastos_tipo.loc[:,['Fuente', 'Destino', 'Monto']]
    
    dfes_sankey = [gastos_grouped, ingresos_grouped, ingresos_tipo, gastos_tipo]
    sankey_data = pd.concat(dfes_sankey)
    sankey_data = sankey_data.reset_index(drop=True)
    
    return sankey_data

@st.cache
def tabla_ultimos_movimientos(df):
    
    last_moves = df.loc[:,['Fecha', 'Monto', 'Tipo', 'Destino']]
    
    last_moves['Fecha'] = last_moves['Fecha'].dt.strftime('%d-%m-%Y')
    
    return last_moves
    
    
    
    
    
    

    
