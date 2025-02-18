import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from src.exception import CustomException
from src.logger import logging

from src.utils import save_object

@dataclass
class DataTranformationConfig:
    preprocessor_ob_file_path=os.path.join('artifacts', "preprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config =DataTranformationConfig()

    def get_data_transfromer_obj(self):

        '''
        This function is responsible for data transformation
        '''
        try:
            numerical_col =  ['reading_score', 'writing_score']
            categorical_col = ['gender', 
                                    'race_ethnicity', 
                                    'parental_level_of_education', 
                                    'lunch', 
                                    'test_preparation_course']
            
            num_pipeline = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ])

            cat_pipeline=Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy = "most_frequent")),
                    ("one_hot_encoding", OneHotEncoder()),
                    ("scaler", StandardScaler(with_mean=False))
                ]
            )

            logging.info(f"Numerical column standard scaling complete: {numerical_col}")
            logging.info(f"Categorical column encoding complete:{categorical_col}")


            preprocessor =ColumnTransformer(
                [
                    ("num_pipleline", num_pipeline, numerical_col),
                    ("cat_pipeline", cat_pipeline, categorical_col)
                ]
            )

            return preprocessor
        
    
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df =pd.read_csv(train_path)
            test_df = pd.read_csv(test_path) 

            logging.info("Read train and test data done")

            logging.info("Obtainning preprocessing object")

            proprocessing_obj = self.get_data_transfromer_obj()

            target_column_name="math_score"
            numerical_col =  ['reading_score', 'writing_score']

            input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]


            logging.info(f"Applying preprocessor object on training dataframe and testing dataframe")

            input_feature_train_array= proprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_array= proprocessing_obj.transform(input_feature_test_df)

            train_arr=np.c_[
                input_feature_train_array, np.array(target_feature_train_df)
            ]

            test_arr=np.c_[
                input_feature_test_array, np.array(target_feature_test_df)
            ]

            logging.info('Saved preprocessing object')

            save_object(
                file_path=self.data_transformation_config.preprocessor_ob_file_path,
                obj=proprocessing_obj
            )

            return(
                train_arr, test_arr, self.data_transformation_config.preprocessor_ob_file_path
            )


        except Exception as e:
            raise CustomException(e, sys)
