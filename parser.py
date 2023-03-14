import pandas as pd
import html
import os
from bs4 import BeautifulSoup

# analiza el texto y elimina todas las etiquetas html

def remove_html_tags(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

file = os.getenv("FILEPATH") #obtiene la ubicacion del archivo desde una variable de entorno
df = pd.read_csv(file, sep=';', index_col=None, header=0, encoding='ISO-8859-1')# carga el archivo csv en un dataframe de pandas
df2 = df.applymap(lambda x: html.unescape(str(x)) if pd.notnull(str(x)) else str(x))# convierte todas las entidades de html en caracteres legibles
df3 = df2.applymap(lambda x: remove_html_tags(str(x)))# usa la funcion lam para eliminar todas las etiquetas de html restantes
df3.to_csv('parsed_file.csv', sep=';', encoding='utf-8-sig', index=False)#guarda el dataframe como un archivo csv con los datos saneados


