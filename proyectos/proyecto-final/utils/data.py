"""
Nombre del archivo: data.py
Autores: Montserrat Lopez, Victor Bassas,  Andres  Henao
Descripción: Archivo que contiene código útil para tranformar datos para
            proyecto de curso Data Scientist de la UOC
Creado: 28/10/2024
Versión: 1.0
Correos: cutmountain@uoc.edu, vbassasb@uoc.edu, ahenaoa@uoc.edu
"""

#importes de librerías externas
import pandas as pd
import numpy as np
import os
import warnings
from sklearn.preprocessing import LabelEncoder

#cash_orig = pd.read_csv('../data/cash_request.csv')
#fees_orig = pd.read_csv('../data/fees.csv')


class Datasets:
    """
    Class for loading and processing the cash and fees datasets.
    It provides methods to create the cash_cohorts DataFrame,
    return the original datasets, and return users by cohort information.
    """

    def __init__(self):
        """
        Initialize the Datasets class by automatically setting paths to the cash and fees CSV files.
        The paths are dynamically generated based on the current working directory.

        Sets:
        - cash_path (str): Path to the cash dataset CSV.
        - fees_path (str): Path to the fees dataset CSV.
        """
        # Get current working directory
        current_path = os.getcwd()

        # Approach 1) Locate the project root directory by finding "monayvi"        
        # Locate the project root directory by finding "monayvi"        
        # aguacate_index = current_path.find("monayvi")
        # if aguacate_index != -1:
        #     project_root = current_path[:aguacate_index + len("monayvi")]
        # else:
        #     raise FileNotFoundError("The directory 'monayvi' was not found in the path.")
        
        # Approach 2) Locate the project root directory by finding "monayvi" or "MONAYVI"              
        # project_name = 'monayvi'
        # aguacate_index = current_path.find(project_name)
        # if aguacate_index == -1:
        #     project_name = project_name.upper()
        #     aguacate_index = current_path.find(project_name)
        # if aguacate_index != -1:
        #     #project_root = current_path[:aguacate_index + len("monayvi")]
        #     project_root = current_path[:aguacate_index + len(project_name)]
        # else:
        #     raise FileNotFoundError("The directory 'monayvi' was not found in the path.")
        
        # Approach 3) Locate the project root directory by finding the last slash "/"
        last_slash_index = current_path.rfind('/')
        if last_slash_index != -1:
            project_root = current_path[:last_slash_index]
        else:
            raise FileNotFoundError("The project directory was not found in the path.")  

        # If we want to check paths externally
        self.cwd = current_path
        self.project_directory = project_root          

        # Set the paths for the cash and fees CSVs
        self.cash_path = os.path.join(project_root, 'data', 'cash_request.csv')
        self.fees_path = os.path.join(project_root, 'data', 'fees.csv')

        # Read the original datasets
        self.dataset_cash_original_df = pd.read_csv(self.cash_path)
        self.dataset_fees_original_df = pd.read_csv(self.fees_path)

        # Initialize the cash and fees DataFrames with copies of the originals...
        self.cash = self.dataset_cash_original_df.copy()
        self.fees = self.dataset_fees_original_df.copy()

        # ... and apply standard treatment:     
        #   cash_request   
        #   - Column cash.id renamed to cash.cash_request_id;
        #   - Column 'id_usurio' added and populated from the combination of cash.user_id and cash.deleted_account_id;
        #   - Column cash.created_at converted to datetime;
        #   - Other columns converted to datetime:
                # created_at (already converted)
                # updated_at
                # moderated_at
                # reimbursement_date
                # cash_request_received_date
                # money_back_date
                # send_at
                # reco_creation
                # reco_last_update        
        #   fees
        #   - Recuperar el valor de 'cash_request_id' a partir de 'reason', para 4 filas con NaN en 'cash_request_id'
        #   - Conversión de 'cash_request_id' de float a int, para poder enlazarlo con la tabla cash
        #   - Columns converted to datetime:
                # created_at
                # updated_at
                # paid_at
                # from_date
                # to_date   
        
        # -- cash_request -----------------------------------------
        # Rename 'id' to 'cash_request_id'
        self.cash.rename(columns={'id': 'cash_request_id'}, inplace=True)

        # Create 'id_usuario' column based on 'user_id' and 'deleted_account_id'
        self.cash['id_usuario'] = self.cash['user_id'].fillna(self.cash['deleted_account_id'])
        self.cash['id_usuario'] = self.cash['id_usuario'].astype(int)

        # Convert 'created_at' to datetime
        self.cash['created_at'] = pd.to_datetime(self.cash['created_at'])        
        self.cash['updated_at'] = pd.to_datetime(self.cash['updated_at'])        
        self.cash['moderated_at'] = pd.to_datetime(self.cash['moderated_at'], format='mixed')        
        self.cash['reimbursement_date'] = pd.to_datetime(self.cash['reimbursement_date'], format='mixed')        
        self.cash['cash_request_received_date'] = pd.to_datetime(self.cash['cash_request_received_date'])        
        self.cash['money_back_date'] = pd.to_datetime(self.cash['money_back_date'], format='mixed')        
        self.cash['send_at'] = pd.to_datetime(self.cash['send_at'], format='mixed')        
        self.cash['reco_creation'] = pd.to_datetime(self.cash['reco_creation'])        
        self.cash['reco_last_update'] = pd.to_datetime(self.cash['reco_last_update'])      

        # -- fees -----------------------------------------
        # Recuperar el valor de 'cash_request_id' a partir de 'reason', para 4 filas con NaN
        extract_crid = lambda x: float(x.split(" ")[-1])
        crid_values = self.fees[self.fees['cash_request_id'].isna()]['reason'].transform(extract_crid)
        reason_dic = { 'cash_request_id' : crid_values}
        self.fees.fillna(reason_dic, inplace=True)

        # Conversión de 'cash_request_id' de float a int, para poder enlazarlo con la tabla cash
        self.fees['cash_request_id'] = self.fees['cash_request_id'].astype(int)        

        # N.B. En lugar de rellenar, podríamos haber optado por el drop() directamente...

        # Opción A) Drop directo en cash
        # Drop de las filas 4 filas de fees sin correspondencia en cash_request, y que además tienen fees.status='cancelled'
        cr_missing = self.fees[self.fees['cash_request_id'].isna()]
        cr_missing
        cr_missing.index #Index([1911, 1960, 4605, 11870], dtype='int64')
        self.fees.drop(index=cr_missing.index, inplace=True)                         

        # Opción B) Drop al hacer el merge (guardo aquí el código que había puesto en merge_tables())
        # Drop de las filas 4 filas de fees (que tenían NaN en 'cash_request_id' y que inicialmente repoblamos), que ahora vemos que no tienen
        #  correspondencia en cash_request, y que además tienen fees.status='cancelled'
        # cr_missing = self.merged[self.merged['cash_request_id'].isna()]
        # cr_missing
        # cr_missing.index #Index([11851, 12255, 12794, 13445], dtype='int64')
        # self.merged.drop(index=cr_missing.index, inplace=True)                

        # Convert to datetime         
        self.fees['created_at'] = pd.to_datetime(self.fees['created_at'])         
        self.fees['updated_at'] = pd.to_datetime(self.fees['updated_at'])         
        self.fees['paid_at'] = pd.to_datetime(self.fees['paid_at'], format='mixed')         
        self.fees['from_date'] = pd.to_datetime(self.fees['from_date'], format='mixed')         
        self.fees['to_date'] = pd.to_datetime(self.fees['to_date'], format='mixed')         

    def merge_tables(self):
        """
        Merge DataFrames 'cash_request' and 'fees', prefixing all columns of 'fees' with 'fee_'
         and on the basis of a 'cash_request_id' common key.

        Returns:
        pd.DataFrame: the result of merging DataFrames 'cash_request' and 'fees'
        """
        # Añadir prefijo a columnas tabla fees
        cash_copy = self.cash.copy()
        fees_copy = self.fees.copy()        
        
        fees_prefixed = fees_copy.add_prefix('fee_')

        merged = pd.merge(cash_copy, fees_prefixed, left_on='cash_request_id', right_on='fee_cash_request_id', how='outer') # 32098 rows

        return merged.copy() # Finally, merged DataFrame has 32094 rows.
    
    def desglose_created_at(self, tabla):
        """
        Desglose de 'created_at'

        Returns:
        pd.DataFrame
        """
        
        df = tabla.copy()

        # Extract datetime features
        df['created_year'] = df['created_at'].dt.year
        df['created_month'] = df['created_at'].dt.month
        df['created_year_month'] = df.apply(lambda row: str(row["created_year"])+'-'+str(row["created_month"]), axis=1)
        df['created_dayofweek'] = df['created_at'].dt.dayofweek + 1  # Monday=0, Sunday=6
        df['created_hour'] = df['created_at'].dt.hour    

        return df

    def get_dummies_and_drop_cols(self, tabla):
        """
        Transforms categorical columns to numerical

        Returns:
        pd.DataFrame: the result of applying get_dummies, OneHotEncoder, LabelEncoder or whatever method best suited to each column
        """

        df = tabla.copy()

        if 'id_usuario' in df.columns:
            # -- cash_request -----------------------------------------
            cash_status_dummies = pd.get_dummies(df.status, dtype="int", drop_first=True, prefix='cstatus', prefix_sep='_')
            cash_transfer_type_dummies = pd.get_dummies(df.transfer_type, dtype="int", drop_first=True, prefix='ctranstype', prefix_sep='_')        
            cash_recovery_status_dummies = pd.get_dummies(df.recovery_status, dtype="int", drop_first=True, prefix='crecostatus', prefix_sep='_')

            # Extract datetime features
            df = self.desglose_created_at(df)       

            labelencoder = LabelEncoder()
            df['created_year_month_dummy'] = labelencoder.fit_transform(df['created_year_month'])       

            concat_dummies = pd.concat([df, cash_status_dummies, cash_transfer_type_dummies, cash_recovery_status_dummies], axis=1)
            concat_dummies.drop(columns=['status','transfer_type','recovery_status','created_year','created_month','created_year_month'], inplace=True) 

        else:
            # -- fees -----------------------------------------
            fees_type_dummies = pd.get_dummies(df.type, dtype="int", drop_first=True, prefix='ftype', prefix_sep='_')
            fees_status_dummies = pd.get_dummies(df.status, dtype="int", drop_first=True, prefix='fstatus', prefix_sep='_')
            # Para poder asignar dummies a category rellenaremos con 'ninguna' los datos faltantes
            #self.merged['fee_category'].fillna('ninguna', inplace=True)
            df.fillna({'category': 'ninguna'}, inplace=True)
            fees_category_dummies = pd.get_dummies(df.category, dtype="int", drop_first=True, prefix='fcategory', prefix_sep='_')        
            fees_charge_moment_dummies = pd.get_dummies(df.charge_moment, dtype="int", drop_first=True, prefix='fchargemoment', prefix_sep='_')

            concat_dummies = pd.concat([df, fees_type_dummies, fees_status_dummies, fees_category_dummies, fees_charge_moment_dummies], axis=1)
            concat_dummies.drop(columns=['type','status','category','charge_moment'], inplace=True)        

        return concat_dummies   
    
    def get_dummies_and_drop_cols(self, tabla, tabla_alias, column):
        """
        Transforms categorical columns to numerical

        Returns:
        pd.DataFrame: the result of applying get_dummies, OneHotEncoder, LabelEncoder or whatever method best suited to each column
        """

        df = tabla.copy()

        column_dummies = pd.get_dummies(df[column], dtype="int", drop_first=True, prefix=tabla_alias+column, prefix_sep='_')

        concat_dummies = pd.concat([df, column_dummies], axis=1)
        concat_dummies.drop(columns=[column], inplace=True) 

        return concat_dummies
    
    # def get_dummies_and_drop_cols(self):
    #     """
    #     Transforms categorical columns to numerical

    #     Returns:
    #     pd.DataFrame: the result of applying get_dummies, OneHotEncoder, LabelEncoder or whatever method best suited to each column
    #     """

    #     # -- cash_request -----------------------------------------
    #     cash_status_dummies = pd.get_dummies(self.merged.status, dtype="int", drop_first=True, prefix='cstatus', prefix_sep='_')
    #     cash_transfer_type_dummies = pd.get_dummies(self.merged.transfer_type, dtype="int", drop_first=True, prefix='ctranstype', prefix_sep='_')        
    #     cash_recovery_status_dummies = pd.get_dummies(self.merged.recovery_status, dtype="int", drop_first=True, prefix='crecostatus', prefix_sep='_')

    #     # Extract datetime features
    #     self.merged['created_year'] = self.merged['created_at'].dt.year
    #     self.merged['created_month'] = self.merged['created_at'].dt.month
    #     self.merged['created_year_month'] = self.merged.apply(lambda row: str(row["created_year"])+'-'+str(row["created_month"]), axis=1)
    #     self.merged['created_dayofweek'] = self.merged['created_at'].dt.dayofweek + 1  # Monday=0, Sunday=6
    #     self.merged['created_hour'] = self.merged['created_at'].dt.hour        

    #     labelencoder = LabelEncoder()
    #     self.merged['created_year_month_dummy'] = labelencoder.fit_transform(self.merged['created_year_month'])

    #     # -- fees -----------------------------------------
    #     fees_type_dummies = pd.get_dummies(self.merged.fee_type, dtype="int", drop_first=True, prefix='ftype', prefix_sep='_')
    #     fees_status_dummies = pd.get_dummies(self.merged.fee_status, dtype="int", drop_first=True, prefix='fstatus', prefix_sep='_')
    #     # Para poder asignar dummies a category rellenaremos con 'ninguna' los datos faltantes
    #     #self.merged['fee_category'].fillna('ninguna', inplace=True)
    #     self.merged.fillna({'fee_category': 'ninguna'}, inplace=True)
    #     fees_category_dummies = pd.get_dummies(self.merged.fee_category, dtype="int", drop_first=True, prefix='fcategory', prefix_sep='_')        
    #     fees_charge_moment_dummies = pd.get_dummies(self.merged.fee_charge_moment, dtype="int", drop_first=True, prefix='fchargemoment', prefix_sep='_')

    #     merged_dummy = pd.concat([self.merged, cash_status_dummies, cash_transfer_type_dummies, cash_recovery_status_dummies,
    #                               fees_type_dummies, fees_status_dummies, fees_category_dummies, fees_charge_moment_dummies], axis=1)
    #     merged_dummy.drop(columns=['status','transfer_type','recovery_status','created_year','created_month','created_year_month',
    #         'fee_type','fee_status','fee_category','fee_charge_moment'], inplace=True)        

    #     return merged_dummy   

    def create_cash_cohorts(self):
        """
        Process the cash DataFrame to create the 'cash_cohorts' DataFrame.

        This method performs the following steps:
        - Renames the 'id' column to 'cash_request_id' in the cash DataFrame.
        - Creates a new 'id_usuario' column based on 'user_id' and 'deleted_account_id'.
        - Converts the 'created_at' column to datetime.
        - Creates a pivot table to group by 'id_usuario' and gets the minimum 'created_at' date.
        - Adds a 'cohorte' column by converting the 'created_at' to period format.
        - Generates readable cohort labels and merges them into the cash DataFrame.
        - Returns the final 'cash_cohorts' DataFrame.

        Returns:
        pd.DataFrame: A DataFrame with the 'cohorte' and 'cohorte_lbl' columns added.
        """
        # # Rename 'id' to 'cash_request_id'
        # self.cash.rename(columns={'id': 'cash_request_id'}, inplace=True)

        # # Create 'id_usuario' column based on 'user_id' and 'deleted_account_id'
        # self.cash['id_usuario'] = self.cash['user_id'].fillna(self.cash['deleted_account_id'])
        # self.cash['id_usuario'] = self.cash['id_usuario'].astype(int)

        # # Convert 'created_at' to datetime
        # self.cash['created_at'] = pd.to_datetime(self.cash['created_at'])

        # Group by 'id_usuario' and find the minimum 'created_at'
        grouped1st = self.cash.pivot_table(
            values="created_at",
            index="id_usuario",
            aggfunc="min"
        )

        # Convert 'created_at' to period (cohorte) and suppress warnings
        warnings.filterwarnings('ignore', category=UserWarning)
        grouped1st['cohorte'] = grouped1st['created_at'].dt.to_period('M')
        warnings.resetwarnings()

        # Create readable cohort labels
        claves = list(np.sort(grouped1st['cohorte'].unique()))
        valores = []
        for index, value in enumerate(claves):
            #valores.append(f'COH-{index + 1:02}.{value.strftime("%b")}')
            valores.append(f'COH-{index+1:02}.{value.strftime("%b")}/{str(value.strftime("%y"))}')

        labels = dict(zip(claves, valores))

        # Merge 'cohorte' information into the original cash DataFrame
        cash_cohorts = pd.merge(self.cash.copy(), grouped1st[['cohorte']], on='id_usuario')

        # Add 'cohorte_lbl' column
        cash_cohorts['cohorte_lbl'] = cash_cohorts['cohorte'].transform(lambda x: labels[x])

        # Convert 'cohorte' column to string for consistency
        cash_cohorts['cohorte'] = cash_cohorts['cohorte'].astype(str)

        return cash_cohorts

    def get_original_datasets(self):
        """
        Return the original cash and fees DataFrames.

        Returns:
        tuple: A tuple containing the original cash DataFrame and the original fees DataFrame.
        """
        return self.dataset_cash_original_df.copy(), self.dataset_fees_original_df.copy()
    
    def get_datasets(self):
        """
        Return minimally treated cash and fees DataFrames (columns converted to Datetime, 'id_usuario' populated, dropped 4 rows in fees)

        Returns:
        tuple: A tuple containing the cash DataFrame and the fees DataFrame.
        """
        return self.cash.copy(), self.fees.copy()

    def get_users_by_cohort(self):
        """
        Calculate the number of users by cohort and return the result.

        This method assumes that the 'cash_cohorts' DataFrame has already been created
        using the 'create_cash_cohorts' method.

        Returns:
        pd.DataFrame: A DataFrame containing the number of unique users for each cohort.
        """
        # First, ensure 'cash_cohorts' is available
        cash_cohorts = self.create_cash_cohorts()

        # Calculate the number of users by cohort
        users_by_cohort = cash_cohorts.groupby('cohorte_lbl')['id_usuario'].nunique().reset_index()
        users_by_cohort.rename(columns={'id_usuario': 'num_usuarios'}, inplace=True)

        # Set 'cohorte_lbl' as the index
        users_by_cohort.set_index('cohorte_lbl', inplace=True)

        return users_by_cohort