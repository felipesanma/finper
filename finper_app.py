# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 11:24:17 2021

@author: Pipe San Martín
"""

import base64
import streamlit as st
from PIL import Image
import datetime


import extractor
import procesamiento
import visualizaciones




def download_csv(df, name='tus_transacciones'):
    
    csv = df.to_csv(index=False)
    base = base64.b64encode(csv.encode()).decode()
    file = (f'<a href="data:file/csv;base64,{base}" download="%s.csv">Descarga tus datos aquí</a>' % (name))
    
    return file


# SETUP ------------------------------------------------------------------------
favicon = Image.open("favicon.ico")
st.set_page_config(page_title='Finper', page_icon = favicon, layout = 'wide', initial_sidebar_state = 'auto')





    
# ROW 1 ------------------------------------------------------------------------
row1_spacer1, row1_1, row1_spacer2, row1_2, row1_spacer3 = st.beta_columns(
        (.1, 2, 1.5, 1, .1)
        )


Title_html = """
    <style>
        .title h1{
          user-select: none;
          font-size: 43px;
          color: white;
          background: repeating-linear-gradient(-45deg, red 0%, yellow 7.14%, rgb(0,255,0) 14.28%, rgb(0,255,255) 21.4%, cyan 28.56%, blue 35.7%, magenta 42.84%, red 50%);
          background-size: 600vw 600vw;
          -webkit-text-fill-color: transparent;
          -webkit-background-clip: text;
          animation: slide 10s linear infinite forwards;
        }
        @keyframes slide {
          0%{
            background-position-x: 0%;
          }
          100%{
            background-position-x: 600vw;
          }
        }
    </style> 
    
    <div class="title">
        <h1>Finper</h1>
    </div>
    """
with row1_1:
    
    st.markdown(Title_html, unsafe_allow_html=True)
    #row1_1.title('Finper')
    st.markdown("_tu **vida financiera** en un **dashboard**_")
    
    
with row1_2:
    st.write('')
    st.markdown("Hecho con :heartbeat: por [Pipe](https://www.linkedin.com/in/pipesanmartin/)")
    


# ROW 2 ------------------------------------------------------------------------


with st.form("User_auth"):
    
    row2_spacer1, row2_1, row2_spacer2, row2_2, row2_spacer3 = st.beta_columns(
    (.1, 1.6, .1, 1.6, .1)
    )
    with row2_1:
    
        fintoc_link = st.text_input('Ingresa tu fintoc link', value="", key='fintoc_link', type="password")
        boton = st.form_submit_button("Traer mis productos financieros")
        
    
    with row2_2:
        
        apikey = st.text_input('y tu apikey', value="", key='apikey', type="password")
    
    #with row2_3:
        
    #    fecha = st.date_input('¿desde qué fecha generamos el dashboard?', datetime.date(2019, 7, 6))
    
    


if boton:
    
    # Haciendo algunos check's
    
    if not apikey or not fintoc_link:
    
        st.warning("Cueeck, ingresa tu apikey o fintoc link")
        st.stop()
    
    
    with st.spinner('Estamos ingresando..'):
        
        try:
            
            data, options = extractor.datos_cuenta(fintoc_link, apikey)
        
        except Exception as e: 
            
            st.error("No se logró la autentificación")
            st.warning(f"Revisa que la apikey: {apikey} y link: {fintoc_link}, sean correctos")
            st.info("Abajo los detalles")
            st.exception(e)
            st.stop()
    
    #st.session_state.fintoc_link = fintoc_link
    #st.session_state.apikey = apikey
    st.session_state.accounts_data = data
    st.session_state.options = options
    
    st.success('¡Ingresamos!')
    
# ROW 3 ------------------------------------------------------------------------


with st.form("User_account"):
        
    row3_spacer1, row3_1, row3_spacer2, row3_2, row3_spacer3 = st.beta_columns((.1, 1.6, .1, 1.6, .1))
    
    with row3_1:
        
        if "options" not in st.session_state:
            
            st.markdown("Obten tu link y apikey de [Fintoc](https://fintoc.com/)")
            st.caption("Y luego haz click en 'Traer mis productos financieros'")
        else:
            
            option = st.radio('Escoge tu cuenta', st.session_state.options, key='option')
            st.caption("Generalmente la opción que contenga '__cuenta__' es la que más usas 🐜")
            
            #st.session_state.option = option
            st.session_state.number_selected = st.session_state.option.split(",")[1].split()[-1]
            st.session_state.nombre_cuenta = st.session_state.option.split(",")[0]
            st.session_state.identificador = st.session_state.accounts_data[st.session_state.accounts_data['number'] == st.session_state.number_selected]['id'].values[0]
            st.session_state.monto_actual = st.session_state.accounts_data[st.session_state.accounts_data['number'] == st.session_state.number_selected]['balance.current'].values[0]
            st.session_state.currency = st.session_state.accounts_data[st.session_state.accounts_data['number'] == st.session_state.number_selected]['currency'].values[0]
            st.session_state.rut = st.session_state.accounts_data[st.session_state.accounts_data['number'] == st.session_state.number_selected]['holder_id'].values[0]
            st.session_state.nombre_prop = st.session_state.accounts_data[st.session_state.accounts_data['number'] == st.session_state.number_selected]['holder_name'].values[0]
        
            
            
            
            json_data = {
                
                "propietario": st.session_state.nombre_prop,
                "rut": st.session_state.rut,
                "nombre_cuenta": st.session_state.nombre_cuenta,
                "N° cuenta": st.session_state.number_selected,
                "currency": st.session_state.currency,
                "disponible": str(st.session_state.monto_actual)
                
                }
            
            st.session_state.json = json_data
            
        boton_2 = st.form_submit_button("Crear mi dashboard")
                
            
    with row3_2:
                
        
        
        if "option" not in st.session_state:
            
            st.caption("🐜")
            
        
        else:
            
            fecha = st.date_input('¿desde qué fecha generamos el dashboard?', datetime.date(2020, 7, 6), key="date")
            #st.session_state.date = fecha
            
            if "json" not in st.session_state:
                
                st.caption("")
            
            else:
                
                st.json(st.session_state.json)
        
if boton_2:
    
    with st.spinner('Estamos recolectando tus datos..'):
        
        try:
            
            todo_movimientos = extractor.extraccion_movimientos(st.session_state.fintoc_link, st.session_state.apikey, st.session_state.identificador, st.session_state.date)
        
        except Exception as e: 
            
            st.error("No los pudimos extraer")
            st.error("Abajo los detalles")
            st.exception(e)
            st.stop()
        
        with st.spinner("Ahora vamos a limpiar los datos"):
            
            try:
            
                df_tmp = procesamiento.crea_dataframe(todo_movimientos)
                df = procesamiento.new_features(df_tmp)
            
            except Exception as e: 
                
                st.error("No logramos limpiarlos")
                st.error("Abajo los detalles")
                st.exception(e)
                st.stop()
            
            with st.spinner("Finalmente los prepararemos para mostrartelos"):
                
                try:
            
                    transactions_date_group, df_daily, df_monthly = procesamiento.transaction_group(df, st.session_state.monto_actual )
                    ingresos_df, ingresos_monthly = procesamiento.ingresos_group(df)
                    gastos_df, gastos_monthly = procesamiento.gastos_group(df)
                    dff, in_dff, out_dff = procesamiento.crea_dff_in_out(df)
                    in_dff_tmp, in_dff_tmp_cum = procesamiento.prepara_para_bar_race(in_dff)
                    out_dff_tmp, out_dff_tmp_cum = procesamiento.prepara_para_bar_race(out_dff)
                    sankey_data = procesamiento.prepara_para_sankey(ingresos_df, gastos_df)
                    last_moves = procesamiento.tabla_ultimos_movimientos(df)
                    st.session_state.readytoshow = True
                
                except Exception as e: 
                    
                    st.error("No logramos prepararlos")
                    st.error("Abajo los detalles")
                    st.exception(e)
                    st.stop()
    
    
    st.session_state.last_moves = last_moves
    st.session_state.ingresos_monthly = ingresos_monthly
    st.session_state.gastos_monthly = gastos_monthly
    st.session_state.df_monthly = df_monthly
    st.session_state.sankey_data = sankey_data
    st.session_state.in_dff_tmp_cum = in_dff_tmp_cum
    st.session_state.out_dff_tmp_cum = out_dff_tmp_cum
    


# ROW 4  ------------------------------------------------------------------------
if "readytoshow" not in st.session_state:
    
    st.caption(" ")
    
else:
    
    
    
    st.plotly_chart(visualizaciones.ingresos_gastos_timeseries(st.session_state.ingresos_monthly, st.session_state.gastos_monthly, st.session_state.df_monthly, st.session_state.currency, st.session_state.date), use_container_width=True)
    
    
    st.plotly_chart(visualizaciones.origen_destino_dinero_sankey(st.session_state.sankey_data, st.session_state.date), use_container_width=True)
    
    row4_1, row4_2 = st.beta_columns((.4, 3))
    
    with row4_2:
        
        st.subheader("Bar Chart Race de ingresos y gastos")
        st.caption("Comparte estos videos con tu ehm..... mejor guardalos para ti")
        
        with st.spinner("Haciendo los videos tipo 'bar chart race'"):
            
            st.write(visualizaciones.race_chart_bar(st.session_state.in_dff_tmp_cum, "Mis ingresos en el tiempo"))
            st.write(visualizaciones.race_chart_bar(st.session_state.in_dff_tmp_cum, "Mis gastos en el tiempo"))
        

# Last ROW  ------------------------------------------------------------------------


    
    rowlast_spacer1, rowlast_1, rowlast_spacer2, rowlast_2, rowlast_spacer3 = st.beta_columns((.1, 1, .1, 2, .1))
    
    with rowlast_1:
        
        st.subheader("Datos de la cuenta")
        st.text(f"Propietario: {st.session_state.json['propietario']}")
        st.text(f"Rut: {st.session_state.json['rut']}")
        st.text(f"Tipo: {st.session_state.json['nombre_cuenta']}")
        st.text(f"N° cuenta: {st.session_state.json['N° cuenta']}")
        st.text(f"Divisa: {st.session_state.json['currency']}")
        st.text(f"Disponible: {st.session_state.json['disponible']}")
        #st.plotly_chart(visualizaciones.indicador_dinero_disponible(st.session_state.monto_actual),use_container_width=True)
    

    with rowlast_2:
        
        st.subheader("Últimas transacciones")
        st.plotly_chart(visualizaciones.plotly_table(st.session_state.last_moves),use_container_width=True)