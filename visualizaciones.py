# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 11:31:37 2021

@author: Pipe San Martín
"""

import bar_chart_race as bcr
import plotly.graph_objects as go
import arrow
from datetime import datetime

def format_title(title, subtitle=None, subtitle_font_size=14):
    title = f'<b>{title}</b>'
    if not subtitle:
        return title
    subtitle = f'<span style="font-size: {subtitle_font_size}px;">{subtitle}</span>'
    return f'{title}<br>{subtitle}'



def ingresos_gastos_timeseries(ingresos_monthly, gastos_monthly, df_monthly, currency, date):
    
    adate = arrow.get(date.strftime('%Y-%m-%d'), 'YYYY-MM-DD')
    new_date = adate.format('DD MMMM (YYYY)', locale='es')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=ingresos_monthly.index,
                             y=ingresos_monthly['Monto'],
                             fill='tozeroy',
                             mode='lines',
                             #mode='none',
                             name='Ingresos',
                             #text=transactions_date_group['Description_monto'],
                             #hoverinfo='x+y+text',
                             line_shape='hv'))
    
    
    
    fig.add_trace(go.Scatter(x=gastos_monthly.index,
                             y=gastos_monthly['Monto'],
                             fill='tozeroy',
                             mode='lines',
                             #mode='none',
                             name='Gastos'))
    
    
    fig.add_trace(go.Scatter(x=df_monthly.index,
                             y=df_monthly['Running balance'].round(0),
                             #fill='tozeroy',
                             mode='lines',
                             #mode='none',
                             name='Balance'))
    
    
    
    
    fig.update_yaxes(hoverformat="$d")
    fig.update_layout(barmode='overlay')
    fig.update_layout(hovermode="x unified")
    fig.update_layout(title=format_title("Mis ingresos y gastos", f"Por mes, a partir del {new_date}"))
    
    return fig
    #fig.show()
    

def origen_destino_dinero_sankey(sankey_data, date):
    
    adate = arrow.get(date.strftime('%Y-%m-%d'), 'YYYY-MM-DD')
    new_date = adate.format('DD MMMM (YYYY)', locale='es')
    
    all_nodes = sankey_data.Fuente.tolist() + sankey_data.Destino.tolist()
    source_indices = [all_nodes.index(area) for area in sankey_data.Fuente]
    target_indices = [all_nodes.index(objetivo) for objetivo in sankey_data.Destino]
    
    
    fig = go.Figure(data=[go.Sankey(
        # Define nodes
        node = dict(
          pad = 20,
          thickness = 20,
          line = dict(color = "black", width = 1.0),
          label =  all_nodes,
          #color =  node_colors,
        ),
    
        # Add links
        link = dict(
          source =  source_indices,
          target =  target_indices,
          value =  sankey_data.Monto,
          #color = node_colors
    ))])
    
    fig.update_layout(title=format_title("Origen y destino de mi dinero", f"TOP 10 acumulado desde el {new_date} hasta hoy"))
    #fig.update_layout(title_text="Origen y destino de mi dinero",
    #                  font_size=10)
    #fig.update_layout(template='plotly_dark')
    return fig
    #fig.show()
    

def indicador_dinero_disponible(monto_actual):
    
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            mode="number",
            value=monto_actual,
            title="Dinero disponible en tu cuenta",
        ))
    
    return fig
    #fig.show()
    
def plotly_table(filter_table, style=True,ancho_columnas=[0.5,0.5,0.5,2]):
    header_values = list(filter_table.columns)
    cell_values = []
    for index in range(0, len(filter_table.columns)):
        cell_values.append(filter_table.iloc[:, index : index + 1])
    if not style:
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(values=header_values), cells=dict(values=cell_values)
                )
            ]
        )
    else:
        fig = go.Figure(
            data=[
                go.Table(
                    #columnorder =[2,2,1],
                    columnwidth = ancho_columnas,
                    header=dict(
                        values=header_values,
                        line_color='darkslategray',
                        align='left',
                        font=dict(color='black'),
                    ),
                    cells=dict(values=cell_values,
                               line_color='darkslategray',
                               align='left',
                               font=dict(color='black')
                               ),
                )
            ]
        )

    fig.update_layout(margin=dict(l=5,r=5,b=10,t=10))
    
    return fig


def race_chart_bar(dff, titulo):
    
    return bcr.bar_chart_race(df=dff,
        orientation='h', 
        sort='desc', 
        n_bars=15, 
        fixed_order=False, 
        fixed_max=True, 
        #steps_per_period=5, 
        period_length=700,
        #interpolate_period=True, 
        period_label={'x': .98, 'y': .3, 'ha': 'right', 'va': 'center'},
        period_fmt='%B %Y',
        period_summary_func=lambda v, r: {'x': .98, 'y': .2, 
                                          's': f'Total: {v.sum():,.0f}', 
                                          'ha': 'right', 'size': 11}, 
        #perpendicular_bar_func='median',  
        title=titulo,
        bar_size=.95,
        )


