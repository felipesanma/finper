# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 11:25:06 2021

@author: Pipe San Martín
"""

from fintoc import Client
import requests
import json as js
import pandas as pd
import streamlit as st


@st.cache
def datos_cuenta(link_fintoc, apikey):

    url = "https://api.fintoc.com/v1/accounts/"

    querystring = {"link_token":link_fintoc}

    headers = {
        "Accept": "application/json",
        "Authorization": apikey
    }

    accounts = requests.request("GET", url, headers=headers, params=querystring)
    
    tmp_accounts = js.loads(accounts.text)

    data = pd.json_normalize(tmp_accounts)
    
    data['Options'] = data['official_name'] + ', N° ' + data['number'] +', Dinero disponible: ' + data['balance.available'].astype(str) +' '+ data['currency']
    
    options = data['Options'].tolist()
    
    return data, options

@st.cache
def extraccion_movimientos(link_fintoc, apikey, account_id, date):
    #Auth
    client = Client(apikey)
    link = client.get_link(link_fintoc)
    
    #Account
    account = link.find(id_=account_id)
    
    #Movements
    movements = account.get_movements(since=date)
    
    #Extract movements and save as a list of move's
    movements_list = []
    for move in movements:

        movements_list.append(str(move))
    
    return movements_list


