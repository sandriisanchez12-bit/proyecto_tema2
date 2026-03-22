import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date,datetime,timedelta

st.set_page_config(page_title='Proyecto Gestor de Mantenimientos')
st.title('Gestor de Mantenimientos')

archivo = 'VehiculosMantenimiento.xlsx'
try:
    df = pd.read_excel(archivo)
except FileNotFoundError:
    st.error('El archivo no se encuentra')
    st.stop()
except Exception as e:
    st.error('Ha ocurrido un error inesperado')
    st.stop()
else:
    st.success(f'Archivo cargado correctamente')


#widgets de filtrado
df['FechaMantenimiento'] = pd.to_datetime(df['FechaMantenimiento'])
st.dataframe(df)
st.write('---')
st.header('Filtrar datos:')

tipos = df['Tipo'].unique()
categorias = df['Categoria'].unique()
#st.write(tipos,categorias)

tipo_sel = st.selectbox('Tipo de vehículo:',['Todos']+list(tipos))
categoria_sel = st.multiselect('Categorías:',list(categorias))
estado_sel = st.radio('Estado',['Todos','Pendiente','Completado'])

km_check = st.checkbox('Filtrar por kilometraje')
km_input = st.number_input('Kilometraje:',100000) if km_check else None

costo_min,costo_max = st.slider(
    'Rango de costo:',
    min_value=30,
    max_value=500,
    value=(100,350)
)

fecha_min = st.date_input('Mostrar registros después de:',)



df_filtrado = df.copy()
if tipo_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Tipo'] == tipo_sel]

if categoria_sel:
    df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categoria_sel)]

if estado_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Estado'] == estado_sel]

if km_check:
    df_filtrado = df_filtrado[df_filtrado['Kilometraje'] >= km_input]

df_filtrado = df_filtrado[
    (df_filtrado['Costo'] >= costo_min) & (df_filtrado['Costo'] <= costo_max)
]

df_filtrado = df_filtrado[
    df_filtrado['FechaMantenimiento'].dt.date >= fecha_min
]

st.subheader('Resultados de filtro')
st.write(f'Registros encontrados {len(df_filtrado)}')
st.dataframe(df_filtrado)




st.header('Formulario')
vh_new = st.text_input('Vehículo:')
tipo_new = st.selectbox('Tipo:',tipos)
fecha_new = st.date_input('Fecha de registro:',value=date.today())
km_new = st.number_input('Kilometraje:', min_value=0)
costo_new = st.number_input('Costo (eur):', min_value=0)
cat_new = st.selectbox('Categoría:',categorias)
estado = st.radio('Estado:',['Pendiente','Completado'])

def generar_codigo():
    ahora = datetime.now() + timedelta(microseconds=1)
    fecha = ahora.strftime('%y%m%d')
    tiempo = ahora.strftime('%H%M%S')
    return f' {fecha},{tiempo}'

if st.button('Registrar mantenimiento'):
    errores = []
    if vh_new.strip() == "":
        errores.append('El vehículo no puede estar vacío')
    if km_new <= 0:
        errores.append('El kilometraje debe ser mayor a 0')
    if costo_new <= 0:
        errores.append('El costo debe ser mayor a 0')
    if fecha_new > date.today():
        errores.append('La fecha no puede ser futura')
    
    if errores:
        st.error(" | ".join(errores))
    else:
        nuevo_codigo = generar_codigo()
        nuevo_registro = {
            'Codigo': nuevo_codigo,
            'Vehiculo': vh_new,
            'Tipo': tipo_new,
            'FechaMantenimiento': fecha_new,
            'Kilometraje':km_new,
            'Costo':costo_new,
            'Categoria':cat_new,
            'Estado':estado
        }
        df = pd.concat([df,pd.DataFrame([nuevo_registro])], ignore_index=True)
        df.to_excel(archivo,index=False)
        st.success(f'Registrado correctamente con el código {nuevo_codigo}')



st.header('Actualizar estado por código:')
codigo_input = st.text_input('Código del mantenimiento:')

if st.button('Marcar completado'):
    if codigo_input.strip() == "":
        st.error('Debe ingresar el código')
    elif codigo_input not in df['Codigo'].values:
        st.error('Código no encontrado')
    else:
        idx = df[df['Codigo'] == codigo_input].index[0]
        if df.loc[idx, 'Estado'] == 'Completado':
            st.info('Este mantenimiento ya está completado')
        else:
            df.iloc[idx,'Estado'] = 'Completado'
            df.to_excel(archivo,index=False)
            st.success('Mantenimiento {codigo_input} marcado como COMPLETADO')
            st.info('Cambio guardado')



st.write('---')
st.header('Gráficos de análisis')

conteo_cat = df['Categoria'].value_counts()
costo_tipo = df.groupby('Tipo')['Costo'].sum()

fig, (ax1,ax2) = plt.subplots(1,2,figsize=(14,5))
ax1.bar(conteo_cat.index, conteo_cat.values)
ax1.set_title('Cantidad de mantenimientos por categoría')
ax1.set_ylabel('Cantidad')
ax1.set_xlabel('Categoría')
ax1.tick_params(axis='x', rotation=40)

ax2.pie(costo_tipo,labels=costo_tipo.index,autopct='%1.1f%%',startangle=90)
ax2.set_title('Distribución de costos por vehículo')

plt.tight_layout()
st.write(fig)
