# Business Payments: EDA and Modelling

Resumen para el proyecto final "Análisis de Business Payments" del curso [UOC](https://www.uoc.edu) Data Scientist.

Versión: 1.0

Creado: 4/12/2024

Autores: Montserrat López Ibáñez


## Descripción

Proyecto de análisis de datos, sobre los cuales se aplicará un modelo de regresión regularizado, así como un modelo de clasificación.

Los datos iniciales son dos datasets relativos a un servicio de préstamos sin interés, pero por los cuales se cobran determinadas cuotas según sea el tipo de préstamo y/o si ha habido retrasos en la devolución del capital solicitado:
- `cash_request.csv`: Contiene las solicitudes de préstamo.
- `fees.csv`: Contiene las cuotas cobradas. 

El excel Lexique-Data_Analyst.xlsx contiene la semántica de los datos.

# Análisis Exploratorio de Datos (EDA)

### Dataset cash_request

El dataset `cash_request` consta de 23.970 filas y 16 columnas, del siguiente tipo:

- **numéricas**: id, amount, user_id, deleted_account_id
- **categóricas**: status, transfer_type, recovery_status
- **datetime**: created_at, updated_at, moderated_at, reimbursement_date, cash_request_received_date, money_back_date, send_at, reco_creation, reco_last_update

Destacaremos la semántica de algunas de estas columnas:

- `id`: identificador de la solicitud de préstamo. Es la columna de enlace con el dataset fees.csv.
- `deleted_account_id`: columna que se pobla cuando el usuario elimina su cuenta.
- `amount`: cantidad solicitada como préstamo.
- `status`: estado del proceso en que se encuentra la solicitud. La ejecución del método value_counts() en esta columna muestra el siguiente resultado:

    ```terminal
    money_back               16397
    rejected                  6568
    direct_debit_rejected      831
    active                      59
    transaction_declined        48
    direct_debit_sent           34
    canceled                    33
    ```

- `transfer_type`: indica el tipo de préstamo solicitado por el usuario, pudiendo ser de tipo instantáneo (el usuario paga una cuota a cambio de que la transferencia sea inmediata) o de tipo regular (el usuario no paga nada y espera el tiempo necesario hasta que la transferencia se hace efectiva).

    ```terminal
    instant    13882
    regular    10088
    ```
- `recovery_status`: indica el estado de los incidentes de pago. Null si no hubo incidentes.

- `moderated_at`: momento en que tuvo lugar una revisión manual de la solicitud.

- `money_back_date`: momento en que el préstamo fue retornado.

### Dataset fees

El dataset `fees` consta de 21.061 filas y 13 columnas, del siguiente tipo:

- **numéricas**: id, cash_request_id, total_amount
- **categóricas**: type, status, category, charge_moment
- **textuales**: reason
- **datetime**: created_at, updated_at, paid_at, from_date, to_date

Destacaremos la semántica de algunas de estas columnas:

- `cash_request_id`: es el identificador que enlaza esta tabla con el dataset cash_request.csv
- `total_amount`: cuota que se le ha cobrado al usuario a cambio de un préstamo de tipo instantáneo, a cambio de un retraso en la devolución del dinero prestado, o a causa de un incidente.
- `type`: tipo de incidente que ha generado el pago de una quota.

    ```terminal
    instant_payment    11099
    postpone            7766
    incident            2196
    ```

- `status`: indica el estado de cobro de la cuota. Cuanto el valor que consta es _accepted_, significa que se cobró con éxito.

    ```terminal
    accepted     14841
    cancelled     4938
    rejected      1194
    confirmed       88
    ```

- `category`: describe el motivo por el cual se cobró una cuota debida a un incidente.

    ```terminal
    rejected_direct_debit     1599
    month_delay_on_payment     597
    ```

- `charge_moment`: momento en que se cargó la cuota siendo _after_ después de haber recibido el préstamo (mayormente préstamos instantáneos, aunque no siempre; también hay incidentes de tipo _postpone_ en que el momento de la cuota es _after_), o bien _before_ cuando la cuota se debe a una solicitud de préstamo regular con algún tipo de incidente.

    ```terminal
    after     16724
    before     4337
    ```

A partir de aquí iniciamos el Análisis Exploratorio de Datos propiamente.

## Calidad de Datos

<!-- 3. **Análisis de Calidad de los Datos**: Evaluar la calidad de los datos, identificando problemas como valores faltantes, inconsistencias, errores o duplicados. -->

El análisis de calidad de datos mostró bastantes valores nulos en ambos datasets. Como ejemplo, mostramos el dataset cash_request.

<img src="./figures/p3/p3_calidad_cash.png" alt="Mapa de calor de valores nulos en cash_request" width="800"/>

A partir de los mapas de calor de valores nulos, observamos lo siguiente:

`cash_request`

- Las columnas `user_id` y `deleted_account_id` son complementarias. De hecho, en un examen más exhaustivo comprobamos que existe 1 fila con valores no nulos tanto en la columna `user_id` como en la columna `deleted_account_id`. No debería darse el caso puesto que la columna `deleted_account_id` sólo tiene valor cuando un usuario ha eliminado su cuenta. ¿Se trata de una cuenta reactivada?
- La columna `moderated_at` presenta bastantes valores no nulos, señal de que ha habido intervención humana en muchas de las solicitudes.

`fees`

- La columna `category` está mayormente por valores nulos. De hecho, comprobamos que tan sólo hay 2.196 valores distintos de Null en esa columna.

## Series de Tiempo

<!-- 1. **Análisis de Series de Tiempo**: Realizar un análisis exhaustivo de las tendencias y patrones temporales presentes en los datos. -->

Si aplicamos la descomposición en Series de Tiempo, por ejemplo, en el dataset `cash_request`, obtendremos los siguientes gráficos para la columna `'id'`.

<img src="./figures/p3/p3_serie_cash_id.png" alt="Serie de Tiempo para cash_request.id" width="950"/>

Aunque ya se percibe una cierta tendencia, no vemos lo que podríamos esperar: en un sistema automático, esperaríamos que los `'id'` fueran consecutivos y en orden ascendente. Para ver si estamos en lo cierto, vamos a aplicar la descomposición nuevamente pero **ordenando previamente los datos a partir de la columna `'created_at'`**.

<img src="./figures/p3/p3_sorted_serie_cash_id.png" alt="Serie de Tiempo ORDENADA para cash_request.id" width="950"/>
<br/><br/>

Ahora sí! Aunque con alguna pequeña anomalía, esto es más lo que esperábamos.

Comprobamos manualmente esa anomalía consistente en algunos valores faltantes para `'id'` entre 5.124 y 5.330:

<img src="./figures/p3/p3_sorted_serie_cash_id_missing.png" alt="Código para mostrar los valores faltantes" width="650" style="margin-left:50px"/>

<img src="./figures/p3/p3_sorted_serie_cash_id_missing_values_highlight.png" alt="Valores faltantes resaltados" width="450" style="margin-left:50px"/>

Por tanto, al hacer el análisis de series de tiempo es importante **ordenar por fecha** para poder observar claramente las tendencias y los patrones temporales presentes en los datos.

La observación más reseñable del análisis de series de tiempo es la tendencia del importe de los préstamos: poco a poco los importes son menores; la gráfica de tendencia va en descenso, lento pero gradual. Los préstamos de 200 se concentran al principio de la serie y luego desaparecen. Igualmente, se observa que los importes descienden de 100 a 50, y finalmente a 25, como valores preponderantes.

<img src="./figures/p3/p3_sorted_serie_cash_amount_trend.png" alt="Serie de Tiempo ORDENADA para cash_request.amount (trend)" width="1024"/>

También, el volumen de `'deleted_account_id'`, que disminuye hacia el final de la serie (esto es interpretable a partir del trazo, más oblicuo al enlazar los últimos valores de la serie). Esto es muy relevante porque significa que la tasa de abandono ya no es tan elevada.

<img src="./figures/p3/p3_sorted_serie_cash_deleted_account_id_trend.png" alt="Serie de Tiempo ORDENADA para cash_request.deleted_account_id (trend)" width="1024"/>


## Columnas Categóricas

<!-- 4. **Análisis Gráfico de los Datos**: Representar gráficamente las variables mediante gráficos como histogramas, diagramas de dispersión, boxplots, entre otros, para facilitar la comprensión visual de los datos. -->

A continuación mostraremos las columnas categóricas de ambas tablas de forma visual.

<img src="./figures/p3/p3_eda_cash_categorical.png" alt="Categóricas en cash_request" width="950"/>
<br/><br/>

Para el dataset cash_request observamos que:

- Se ha recuperado el dinero prestado para un 68,4% de las solicitudes.
- El porcentaje de solicitudes de tipo _instant_ es mayor que las de tipo _regular_, con casi un 58% frente a un 42%.
- De aquellas solicitudes que presentaron incidentes de pago en el momento del reembolso, un 74% de los incidentes se resolvieron satisfactoriamente.
<br/><br/>

<img src="./figures/p3/p3_eda_fees_categorical.png" alt="Categóricas en fees" width="800"/>
<br/><br/>

Para el dataset fees observamos que:

- Una gran proporción de las cuotas cobradas (52,7%) corresponde a solicitudes de préstamo de tipo _instant_, donde el usuario recibe el dinero de forma inmediata a cambio de esa cuota.
- A pesar de que la mayor parte de cuotas han sido aceptadas por el usuario (70%), existe un volumen significativo de cuotas canceladas (23,4%). Aunque según la documentación, es posible que parte de éstas sean debidas a ajustes manuales.
- El motivo para cobrar la cuota se debe principalmente (72,8%) a que el cargo a la tarjeta de crédito en el momento de reembolso del préstamo fue rechazado.
- El momento en que se cobra la cuota está distribuido en un 80%-20% para las que se cobran después de haber recibido el préstamo, _after_, con respecto a las que se cobran antes de haberlo recibido, _before_.

## Columnas Numéricas

En cuanto a las columnas numéricas, las únicas de interés son `'amount'` y `'total_amount'`, en el dataset `cash_request` y en el `fees` respectivamente.

<img src="./figures/p3/p3_eda_cash_numerical.png" alt="Numéricas en cash_request" width="1200"/>
<br/><br/>

Debido al gran volumen de solicitudes y cuotas de un mismo importe, los gráficos anteriores nos ocultan valores cuya frecuencia es mucho menor. Es por esto que necesitamos mostrarlos mediante gráficas de caja o de violín.

<img src="./figures/p3/p3_eda_cash_violin.png" alt="Violin en cash_request" width="1024"/>
<br/><br/>

Ahora sí vemos claramente los valores atípicos en 200.

Lo mismo ocurre con el dataset `fees`, donde el valor atípico de 10 queda oculto en el histograma.

<img src="./figures/p3/p3_eda_fees_numerical.png" alt="Numéricas en fees" width="1200"/>
<br/><br/>

En este caso el boxplot es suficiente para resaltar claramente ese valor atípico.

<img src="./figures/p3/p3_eda_fees_box.png" alt="Boxplot en fees" width="1024"/>
<br/><br/>

Aí, la observación de los gráficos anteriores revela lo siguiente:

- La mayor parte de solicitudes son de 100, 50 y 25, tal y como corroboramos con un `value_counts()`. También observamos un pequeño grupo de solicitudes de 200.

```terminal
amount
100.0    16094
50.0      5304
25.0      1276
80.0       267
60.0       190
70.0       151
20.0       132
30.0       114
40.0       100
90.0        91
10.0        57
200.0       25
95.0        21
```

- En cuanto a las cuotas, todas son de 5 a excepción de una que es de 10.

```terminal
total_amount
5.0     21060
10.0        1
```

## Relaciones entre Columnas Numéricas

<!-- 2. **Análisis Exploratorio de Datos (EDA)**: Identificar patrones, anomalías y relaciones entre las variables mediante visualizaciones y estadísticas descriptivas. -->
<!-- 6. **Análisis de Correlación**: Evaluar las relaciones y asociaciones entre las variables mediante matrices de correlación y análisis de dependencias. -->
<!-- 7. **Análisis de Outliers**: Detectar y tratar los valores atípicos (outliers) presentes en los datos para mejorar la precisión de los modelos. -->

Los gráficos de dispersión nos permiten ver posibles relaciones entre las distintas variables numéricas.

<img src="./figures/p3/p3_eda_cash_dispersion.png" alt="Dispersión en cash_request" width="1024"/>
<br/><br/>

A parte de confirmar las observaciones de los gráficos de histograma, caja, y violín, los gráficos de dispersión también revelan esa anomalía que ya habíamos observado en una de las filas de cash_request entre `'user_id'` y `'deleted_account_id'`.
<br/><br/>

<img src="./figures/p3/p3_eda_fees_dispersion.png" alt="Dispersión en fees" width="1024"/>
<br/><br/>

Los gráficos de dispersión para fees nos muestran claramente el valor atípico de 10 en `'total_amount'`, así como una relación entre `'cash_request_id'` y `'id'` ya que una misma solicitud puede asociarse a más de una cuota debido a distintos incidentes o retrasos en el pago.

<img src="./figures/p3/p3_eda_cash_correlation.png" alt="Correlación en cash_request" width="800"/>
<br/><br/>
<img src="./figures/p3/p3_eda_fees_correlation.png" alt="Correlación en fees" width="800"/>

# Análisis de Cohortes

<!-- 5. **Segmentación Inteligente de los Datos**: Implementar técnicas de segmentación avanzadas que aporten valor al análisis y la extracción de insights relevantes. -->
<!-- 8. **Análisis de Cohortes Avanzados**: Realizar segmentación y análisis del comportamiento de los usuarios a lo largo del tiempo, con el objetivo de identificar patrones de retención, uso y otros comportamientos clave. -->

<!-- 9. **Modelos de Regresión Regularizados**: Implementar modelos de regresión regularizados (como Ridge, Lasso, ElasticNet), utilizando técnicas de búsqueda de hiperparámetros para optimizar el rendimiento del modelo. -->
<!-- 10. **Modelos de Clasificación**: Desarrollar y optimizar modelos de clasificación (como árboles de decisión, SVM, k-NN), utilizando los métodos adecuados de validación y evaluación. -->
<!-- 11. **Validación de Modelos**: Seleccionar los mejores modelos mediante validación cruzada con k-fold, para asegurar la robustez y generalización de los modelos creados. -->
<!-- 12. **Uso de Scraping para Variables Exógenas**: El proyecto debe incluir el uso de técnicas de web scraping para obtener variables adicionales de fuentes externas que aporten valor a los datos originales del proyecto. -->



![Tipo de adelante según cohorte](figures/metricas_tipo_adelanto.png)

<img src="./figures/reg_coefs.png" alt="Intercepto y Coeficientes para la Regresión Lineal" width="450" style="margin-left:50px"/>

