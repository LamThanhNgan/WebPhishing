import pickle
from sklearn import preprocessing
import numpy as np
from Phishpedia.phishpedia.phishpedia_config import load_config
from Phishpedia.phishpedia.phishpedia_main import runit


def convertData(data): 
    for col in data.columns:
        col_type = data[col].dtype
        if col_type == 'object' or col_type == 'bool' :
        
            label_encoder = preprocessing.LabelEncoder()
            # Encode labels in column 'species'.
            data[col]= label_encoder.fit_transform(data[col])
    return data


def static_prediction(result):
    #Passing data to model & loading the model from disks
    model_path = 'ml_model_src/model_static.pkl'
    classifier = pickle.load(open(model_path, 'rb'))
    prediction = classifier.predict([result])[0]
    conf_score =  np.max(classifier.predict_proba([result]))*100
    error = '0'
    message = 'Successfull'
    return {"model_path": model_path, "classifier": classifier, "prediction": prediction, "conf_score": conf_score, "error": error,  "message": message}

def dynamic_predictions(folder_result_name):
    # url_path = folder_result_name+"/info.txt"
    # screenshot_path = folder_result_name + "/shot.png"

    cfg_path = None # None means use default config.yaml
    reload_targetlist = False
    ELE_MODEL, SIAMESE_THRE, SIAMESE_MODEL, LOGO_FEATS, LOGO_FILES, DOMAIN_MAP_PATH = load_config(cfg_path, reload_targetlist)
    # phish_category, pred_target, plotvis, siamese_conf, pred_boxes = test(url_path, screenshot_path,
    #                                                                   ELE_MODEL, SIAMESE_THRE, SIAMESE_MODEL, LOGO_FEATS, LOGO_FILES, DOMAIN_MAP_PATH)
    phish_category, phish_target, siamese_conf, vt_result, img_path = runit( folder_result_name, ELE_MODEL, SIAMESE_THRE, SIAMESE_MODEL, LOGO_FEATS, LOGO_FILES, DOMAIN_MAP_PATH )
    return {"prediction": phish_category, "brand_name": phish_target, "conf_score": siamese_conf, "virustotal": vt_result,"image_result": img_path}




