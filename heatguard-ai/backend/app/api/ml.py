"""
HeatGuard AI — ML Router
"""
from fastapi import APIRouter
from app.schemas.schemas import MLPredictRequest, MLPredictResponse
from app.ml.prediction.predict import predict_risk, get_model_info, load_model, is_model_loaded
from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.post("/predict", response_model=MLPredictResponse)
def ml_predict(request: MLPredictRequest):
    """
    Run ML risk prediction.
    
    If heat_index, wbgt, htsi are not provided, they are calculated
    from the provided weather inputs automatically.
    """
    # Calculate derived thermal metrics if not provided
    heat_index = request.heat_index
    wbgt = request.wbgt
    htsi = request.htsi

    if heat_index is None or wbgt is None or htsi is None:
        wx = WeatherInput(
            temperature=request.temperature,
            humidity=request.humidity,
            wind_speed=request.wind_speed,
            solar_radiation=request.solar_radiation,
            heatwave_duration=request.heatwave_duration,
        )
        thermal = calculate_all_thermal_metrics(wx)
        heat_index = heat_index or thermal.heat_index
        wbgt = wbgt or thermal.wbgt
        htsi = htsi or thermal.htsi

    features = {
        "temperature": request.temperature,
        "humidity": request.humidity,
        "wind_speed": request.wind_speed,
        "solar_radiation": request.solar_radiation,
        "heat_index": heat_index,
        "wbgt": wbgt,
        "htsi": htsi,
        "temperature_anomaly": request.temperature_anomaly,
        "heatwave_duration": float(request.heatwave_duration),
        "population_density": request.population_density,
        "elderly_density": request.elderly_density,
        "outdoor_worker_density": request.outdoor_worker_density,
        "historical_health_indicator": request.historical_health_indicator,
        "vulnerability_score": request.vulnerability_score,
    }

    result = predict_risk(features)
    return MLPredictResponse(**result)


@router.get("/model-info")
def get_model_info_endpoint():
    """Get information about the currently loaded ML model."""
    return get_model_info()


@router.post("/train")
def trigger_training():
    """Trigger model retraining (admin use). Returns metadata."""
    from app.ml.training.train import train_and_save_model
    try:
        metadata = train_and_save_model()
        load_model()  # Reload the newly trained model
        return {
            "status": "success",
            "message": "Model trained successfully on synthetic demonstration data",
            "metadata": metadata,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
