# Business Payments: EDA and Modelling

Resumen ejecutivo para el proyecto final "Análisis de Business Payments" del curso [UOC](https://www.uoc.edu) Data Scientist.

Versión: 1.0

Creado: 4/12/2024

Autores: Montserrat López Ibáñez


## Descripción

Proyecto de análisis de datos, sobre los cuales se aplicará un modelo de regresión regularizado, así como un modelo de clasificación.

Los datos iniciales son dos datasets:
- `cash_request.csv`: Contiene las solicitudes de préstamo.
- `fees.csv`: Contiene las cuotas cobradas 

El excel Lexique-Data_Analyst.xlsx contiene la semántica de los datos.

## Análisis Exploratorio de Datos (EDA)

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


OBSERVACIONES:

Existe 1 fila con valor tanto en la columna `user_id` como en la columna `deleted_account_id`.


