import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from skl2onnx.common.data_types import FloatTensorType
from onnxmltools.convert import convert_xgboost
import onnx

def main():
    print("Cargando dataset...")
    df = pd.read_csv('../OmniApex_Dataset.csv')
    
    # Feature Engineering
    features = [
        'Signal_Type', 
        'Micro_Velocity', 
        'Micro_Acceleration', 
        'Macro_Velocity', 
        'Tension_Ratio', 
        'Hour_of_Day', 
        'Day_of_Week', 
        'Dist_SMA200',
        'Session_Vol_Ratio'
    ]
    X = df[features].astype(np.float32)
    y = df['Target_Label'].astype(np.int64)
    
    print(f"Total datos: {len(df)}")
    print(f"DistribuciÃƒÂ³n original:\n{y.value_counts()}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Entrenando XGBoost Classifier...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    # IMPORTANTE: Usar .values para evitar que XGBoost guarde nombres de features ("ADX_Value", etc)
    # Ya que el convertidor de ONNX espera nombres en formato "f0", "f1", etc.
    model.fit(X_train.values, y_train.values)
    
    print("\nEvaluando modelo (Threshold 0.65)...")
    y_prob = model.predict_proba(X_test.values)[:, 1]
    THRESHOLD = 0.65
    y_pred = (y_prob >= THRESHOLD).astype(int)
    
    print(classification_report(y_test, y_pred))
    print("Matriz de confusiÃƒÂ³n:\n", confusion_matrix(y_test, y_pred))
    
    # Exportar a ONNX
    print("\nConvirtiendo a ONNX...")
    from skl2onnx import update_registered_converter
    from skl2onnx.common.shape_calculator import calculate_linear_classifier_output_shapes
    from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost as convert_xgb
    
    long_shape = [1, 9]
    update_registered_converter(
        XGBClassifier, 'XGBoostXGBClassifier',
        calculate_linear_classifier_output_shapes, convert_xgb,
        options={'nocl': [True, False], 'zipmap': [True, False, 'columns']})
        
    from skl2onnx import to_onnx
    
    # IMPORTANTE: Desactivar zipmap para que MetaTrader 5 pueda leer el tensor de probabilidades como float array
    onx = to_onnx(model, X_train[:1].values.astype(np.float32), 
                  target_opset={'': 12, 'ai.onnx.ml': 3},
                  options={'zipmap': False})
    
    onnx_path = "../OmniApex_MetaModel.onnx"
    with open(onnx_path, "wb") as f:
        f.write(onx.SerializeToString())
        
    print(f"Ã¢Å“â€¦ Modelo guardado en: {onnx_path}")

if __name__ == "__main__":
    main()
