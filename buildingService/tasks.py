from .serializers import BuildingSerializer, CooperationSerializer
from .utils import get_latest_file_from_s3, download_file_from_s3
from .models import Building, Cooperation
from django.db import transaction
import pandas as pd
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="processBuildingData")
def processBuildingData():
    bucket = "buildingdumps"
    latest_file_key = get_latest_file_from_s3(bucket)
    if latest_file_key is None:
        return "No files found in the bucket."

    local_file_path = "/app/latest_buildings_info.csv"
    download_successful = download_file_from_s3(
        bucket, latest_file_key, local_file_path
    )
    if not download_successful:
        return "Failed to download the latest file."

    df = pd.read_csv(local_file_path, low_memory=False)
    batch_size = 1000
    total_rows = len(df)
    num_batches = 100

    for batch in range(num_batches):
        start_index = batch * batch_size
        end_index = min((batch + 1) * batch_size, total_rows)
        rows = df.iloc[start_index:end_index].to_dict(orient="records")
        processBuildingDataBatch.delay(rows, batch, num_batches)

    return "Processing building data in batches"

@shared_task(name="processBuildingDataBatch")
def processBuildingDataBatch(rows, batch, num_batches):
    logger.info(f"Processing batch {batch + 1} of {num_batches}...")
    cooperation_batch_data = []
    building_instances = []

    for row in rows:
        try:
            building_data = {
                "name": row["name"],
                "address": row["address"],
                "city": row["city"],
                "state": row["state"],
                "description": row["description"],
                "latitude": row["lat"],
                "longitude": row["lng"],
                "zip": row["zip"],
                "website": row["website"],
                "phone": row["phone"],
                "neighborhood": row["neighborhood_name"],
            }

            building_serializer = BuildingSerializer(data=building_data)
            if building_serializer.is_valid():
                building = building_serializer.save()
                building_instances.append(building)

                # Process Cooperation after building is successfully saved
                cooperation_data = {
                    "cooperate": row.get("cooperate"),
                    "cooperation_fixed": row.get("cooperation_fixed"),
                    "cooperation_percentage": row.get("cooperation_percentage"),
                }
                cooperation_serializer = CooperationSerializer(data=cooperation_data)
                if cooperation_serializer.is_valid():
                    cooperation = cooperation_serializer.save(building=building)
                    cooperation_batch_data.append(cooperation)
                else:
                    logger.error(
                        f"Cooperation data validation failed: {cooperation_serializer.errors}"
                    )
            else:
                logger.error(
                    f"Building data validation failed: {building_serializer.errors}"
                )
                continue

        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")

    try:
        with transaction.atomic():
            # Since buildings and cooperation are saved, no need to save again, just log success
            logger.info(
                f"Transaction successful for batch {batch + 1} of {num_batches}"
            )
    except Exception as e:
        logger.error(f"Transaction failed: {str(e)}")
