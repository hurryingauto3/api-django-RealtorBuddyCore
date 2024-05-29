from .serializers import BuildingSerializer, CooperationSerializer
from .models import Building, Cooperation
from django.db import transaction
import pandas as pd
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(name="processBuildingData")
def processBuildingData():
    df = pd.read_csv("/app/buildings_info.csv", low_memory=False)
    batch_size = 1000
    total_rows = len(df)
    # num_batches = (total_rows + batch_size - 1) // batch_size
    num_batches = 100

    for batch in range(num_batches):
        start_index = batch * batch_size
        end_index = min((batch + 1) * batch_size, total_rows)

        rows = df.iloc[start_index:end_index].to_dict(orient="records")
        process = processBuildingDataBatch.delay(rows, batch, num_batches)

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
            else:
                logger.error(
                    f"Building data validation failed: {building_serializer.errors}"
                )
                continue  # Skip this building and its associated cooperation if building fails

            cooperation_data = {
                "building": building.id,  # Link the building ID here
                "cooperate": row.get("cooperate"),
                "cooperation_fixed": row.get("cooperation_fixed"),
                "cooperation_percentage": row.get("cooperation_percentage"),
            }

            cooperation_serializer = CooperationSerializer(data=cooperation_data)
            if cooperation_serializer.is_valid():
                cooperation = cooperation_serializer.save()
                cooperation_batch_data.append(cooperation)
            else:
                logger.error(
                    f"Cooperation data validation failed: {cooperation_serializer.errors}"
                )

        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
    try:
        with transaction.atomic():
            # Since buildings are already saved, you only need to save the cooperation batch
            Cooperation.objects.bulk_create(
                cooperation_batch_data, ignore_conflicts=True
            )
            logger.info(
                f"Transaction successful for batch {batch + 1} of {num_batches}"
            )
    except Exception as e:
        logger.error(f"Transaction failed: {str(e)}")
