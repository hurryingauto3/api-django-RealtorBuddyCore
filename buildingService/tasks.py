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
    building_batch_data = []
    for row in rows:
        building_data = {
            "name": row["name"] if pd.notnull(row["name"]) else None,
            "address": row["address"] if pd.notnull(row["address"]) else None,
            "city": row["city"] if pd.notnull(row["city"]) else None,
            "state": row["state"] if pd.notnull(row["state"]) else None,
            "description": (
                row["description"] if pd.notnull(row["description"]) else None
            ),
            "latitude": row["lat"] if pd.notnull(row["lat"]) else None,
            "longitude": row["lng"] if pd.notnull(row["lng"]) else None,
            "zip": row["zip"] if pd.notnull(row["zip"]) else None,
            "website": row["website"] if pd.notnull(row["website"]) else None,
            "phone": row["phone"] if pd.notnull(row["phone"]) else None,
            "neighborhood": (
                row["neighborhood_name"]
                if pd.notnull(row["neighborhood_name"])
                else None
            ),
            # Add other building fields as needed
        }

        cooperation_data = {
            "cooperate": row["cooperate"] if pd.notnull(row["cooperate"]) else None,
            "cooperation_fixed": (
                row["cooperation_fixed"]
                if pd.notnull(row["cooperation_fixed"])
                else None
            ),
            "cooperation_percentage": (
                row["cooperation_percentage"]
                if pd.notnull(row["cooperation_percentage"])
                else None
            ),
        }

        try:
            building_serializer = BuildingSerializer(data=building_data)
            cooperation_serializer = CooperationSerializer(data=cooperation_data)

            if not building_serializer.is_valid():
                logger.error(
                    f"Building data validation failed for row {row}: {building_serializer.errors}"
                )
            else:
                building = building_serializer.save()
                building_batch_data.append(building)

            if not cooperation_serializer.is_valid():
                logger.error(
                    f"Cooperation data validation failed for row {row}: {cooperation_serializer.errors}"
                )
            else:
                cooperation_batch_data.append(cooperation_serializer.validated_data)

        except Exception:
            logger.error(f"Error processing row {row}")

    try:
        with transaction.atomic():
            # Process building and cooperation data here
            buildings = Building.objects.bulk_create(
                building_batch_data, ignore_conflicts=True
            )
            cooperations = [
                Cooperation(building=building, **data)
                for building, data in zip(buildings, cooperation_batch_data)
            ]
            Cooperation.objects.bulk_create(cooperations)
            logger.info(
                f"Transaction successful for batch {batch + 1} of {num_batches}"
            )
    except Exception as e:
        logger.error(
            f"Transaction failed for batch {batch + 1} of {num_batches}: {str(e)}"
        )
