from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator


# 1. Define the DAG structure using the @dag decorator
@dag(
    start_date=datetime(2026, 1, 1),
    schedule="@daily", 
    catchup=False,
    tags=["example"]
)
def simple_etl_pipeline():
    @task.bash
    def clean_logs():
        return "rm -rf /opt/airflow/logs/*"
    # 2. Define individual tasks using the @task decorator
    @task
    def extract_data():
        return {"data": [10, 20, 30, 40]}

    

    @task
    def transform_data(raw_data: dict):
        # Multiply all data entries by 2
        transformed = [x * 2 for x in raw_data["data"]]
        print(transformed)
        return transformed

    @task
    def load_data(final_data: list):
        print(f"Successfully loaded data: {final_data}")

    # 3. Create the pipeline dependency chain by passing python variables
    clean_logs=clean_logs()
    data = extract_data()
    cleaned_data = transform_data(data)
    load_data(cleaned_data)

# Instantiate the pipeline
simple_etl_pipeline()
