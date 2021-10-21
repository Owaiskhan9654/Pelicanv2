import psycopg2
import pandas as pd
from pprint import pprint
import numpy as np
import joblib
from scipy.stats import kurtosis, skew, variation, iqr, entropy, power_divergence, moment,jarque_bera

def feature_extraction_from_database(sample_id):
    # establishing the connection
    conn = psycopg2.connect(
        database="pelican", user='owais.ahmed@canarydetect.com', password='bLHshTcQ65fe8AnZ',
        host='canary-pelican-db-analytics-trials.cyeuxkq1eajh.us-east-1.rds.amazonaws.com', port='5432'
    )

    cursor = conn.cursor()

    query = 'select "sample_id","id", "channel", "data", "type" from sample_data where sample_id = {}'.format(sample_id)
    
    cursor.execute(query)
    sample_data_list = cursor.fetchall()

    
    RawC1C2 = pd.DataFrame()
    for sample_data in sample_data_list:
        df1=pd.DataFrame(sample_data[3],columns=[sample_data[2]+" "+sample_data[4]])
        RawC1C2=pd.concat([RawC1C2,df1],axis=1)

    # Closing the connection
    conn.close()
    #df = df.reindex(['C1 control','C1 test','C2 control','C2 test'], axis=1)
    if RawC1C2['C1 control'].empty or RawC1C2['C1 test'].empty or RawC1C2['C2 control'].empty or RawC1C2['C2 test'].empty:
        final_prediction = "Either or All Channel Data is Not Present"
        return final_prediction
    RawC1C2['C1']=(RawC1C2['C1 control']+RawC1C2['C1 test'])/2
    RawC1C2['C2']=(RawC1C2['C2 control']+RawC1C2['C2 test'])/2
    
    features = []
    for i in RawC1C2[['C1','C2']].columns:

        minValue = RawC1C2[i].min()
        maxValue = RawC1C2[i].max()
        Peak_height = max(RawC1C2[i]) - min(RawC1C2[i])
        peak_time = RawC1C2[i].idxmax() - RawC1C2[i].idxmin()
        area = np.trapz(RawC1C2[i], x=(RawC1C2[i].index))
        Kurtosis = kurtosis(RawC1C2[i])
        Skew = skew(RawC1C2[i])
        Variation = variation(RawC1C2[i])
        Mean_Absolute_Deviation = RawC1C2[i].mad()
        Percentile5th = np.percentile(RawC1C2[i], 5)
        Percentile95th = np.percentile(RawC1C2[i], 95)
        IQR = iqr(RawC1C2[i])
        Jarque_bera = jarque_bera(RawC1C2[i])
        Jarque_bera = Jarque_bera[0]
        Moment = moment(RawC1C2[i], moment=3)
        Mean = RawC1C2[i].mean()
        Std = RawC1C2[i].std()
        # Coefficient of Variation = (Standard Deviation / Mean) * 100.
        Coeff_of_variation = (Std/Mean*100)

        features.append([sample_id,i, Mean, Std, Peak_height, peak_time, minValue, maxValue, area, Kurtosis, Skew, Moment,
                         Variation, Percentile5th, Percentile95th, Mean_Absolute_Deviation, IQR, Jarque_bera,
                         Coeff_of_variation])
    feature_dataset = pd.DataFrame(features, columns=['Sample ID','Electrode', 'Mean', 'Standard_Deviation', 'Peak_height',
                                                      'Peak_time', 'Min Value', 'Max Value', 'Area', 'Kurtosis', 'Skew',
                                                      'Moment', 'Variation', 'Percentile5th', 'Percentile95th',
                                                      'Mean_Absolute_Deviation', 'IQR', 'Jarque_bera', 'Coeff_of_variation'])
    
    df_test = feature_dataset
    #d1 = {'C1': 10, 'C2': 20}
    #df_test['Electrode'] = df_test['Electrode'].map(d1)
    model = joblib.load("random_forest.joblib")
    #df_test['Predictions'] = model.predict(df_test.iloc[:,2:]).astype(np.float32)
    #df_test['Probability_Prediction'] = model.predict_proba(df_test.iloc[:,2:].astype(np.float32))[:, 1]
    df_predict=pd.DataFrame(model.predict_proba(df_test.iloc[:,2:]),columns=["Inconclusive Probability Percentage","Negative Probability Percentage","Positive Probability Percentage"])*100
    df_predict["Predictions on Channels"]=model.predict(df_test.iloc[:,2:])
    df_predict["Predictions on Channels"]=df_predict["Predictions on Channels"].map({-1:"Inconclusive Channel",0:"Negative Channel",1:"Positive Channel"})
    df_predict.insert(0,"Electrode",list(df_test["Electrode"]))
    df_predict.insert(1, "Sample ID", [sample_id,sample_id])
    
    if pd.DataFrame(df_predict[["Inconclusive Probability Percentage", "Negative Probability Percentage", "Positive Probability Percentage"]].max(axis=0)).idxmax().values[0] == 'Negative Probability Percentage':
        final_prediction = "Final Prediction is Negative"
    elif pd.DataFrame(df_predict[["Inconclusive Probability Percentage", "Negative Probability Percentage", "Positive Probability Percentage"]].max(axis=0)).idxmax().values[0] == 'Positive Probability Percentage':
        final_prediction = "Final Prediction is Positive"
    elif pd.DataFrame(df_predict[["Inconclusive Probability Percentage", "Negative Probability Percentage", "Positive Probability Percentage"]].max(axis=0)).idxmax().values[0] == 'Inconclusive Probability Percentage':
        final_prediction = "Final Prediction is Inconclusive"



    return df_predict, final_prediction
    
