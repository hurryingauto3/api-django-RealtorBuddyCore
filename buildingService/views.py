from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .utils import update_address_abbreviations
from .serializers import BuildingSerializer, CooperationSerializer
from .models import Building, AddressAbbreviation, Cooperation
from django.db.models import Q
from django.db import transaction
import pandas as pd

from logging import getLogger


logger = getLogger(__name__)


def index(request):
    return HttpResponse("Realtor Buddy - Building Service")


def convertAndInsertBuildingData(request):
    df = pd.read_csv("/app/buildings_info.csv", low_memory=False)
    batch_size = 50
    total_rows = len(df)
    num_batches = 10

    for batch in range(num_batches):
        start_index = batch * batch_size
        end_index = min((batch + 1) * batch_size, total_rows)
        cooperation_batch_data = []
        building_batch_data = []

        for _, row in df.iloc[start_index:end_index].iterrows():
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
                # Add other building fields as needed
            }

            cooperation_data = {
                "cooperate": row["cooperate"],
                "fixed": True if row["cooperation_fixed"] else False,
                "value": (
                    row["cooperation_percentage"]
                    if row["cooperation_percentage"]
                    else row["cooperation_fixed"] if row["cooperation_fixed"] else None
                ),
            }

            try:
                building_serializer = BuildingSerializer(data=building_data)
                cooperation_serializer = CooperationSerializer(data=cooperation_data)

                if building_serializer.is_valid():
                    building = building_serializer.save()
                    building_batch_data.append(building)
                    if cooperation_serializer.is_valid():
                        cooperation_batch_data.append(
                            cooperation_serializer.validated_data
                        )

            except Exception:
                continue

        with transaction.atomic():
            buildings = Building.objects.bulk_create(building_batch_data, ignore_conflicts=True)
            cooperations = [
                Cooperation(building=building, **data)
                for building, data in zip(buildings, cooperation_batch_data)
            ]
            Cooperation.objects.bulk_create(cooperations)

        logger.info(f"Batch {batch + 1} of {num_batches} completed.")

    return HttpResponse("Building data inserted successfully")

def updateAddressAbbreviations(request):

    abbr_dict = update_address_abbreviations()
    directions_mapping = {
        "n": ["north"],
        "s": ["south"],
        "e": ["east"],
        "w": ["west"],
        "ne": ["northeast"],
        "nw": ["northwest"],
        "se": ["southeast"],
        "sw": ["southwest"],
    }

    abbr_dict = {**abbr_dict, **directions_mapping}
    AddressAbbreviation.update_abbreviations(abbr_dict)
    return HttpResponse("Update Address Abbreviations")


class BuildingViewSet(viewsets.ModelViewSet):
    serializer_class = BuildingSerializer
    queryset = Building.objects.all()

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        if isinstance(serializer.validated_data, list):
            # Bulk creation
            buildings = [Building(**item) for item in serializer.validated_data]
            Building.objects.bulk_create(buildings)

            # Create Cooperation object for each building
            cooperations = [
                Cooperation(building=building, **item.get("cooperation", {}))
                for building, item in zip(buildings, serializer.validated_data)
                if item.get("cooperation")
            ]
            Cooperation.objects.bulk_create(cooperations)
        else:
            # Single creation
            serializer.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        if search is not None:
            search_terms = search.split()
            # Create a list to store the Q objects for each search term
            q_objects = []
            for term in search_terms:
                # Check if the term is a state abbreviation
                if len(term) == 2 and term.isalpha() and term.isupper():
                    q_objects.append(Q(state__iexact=term))
                else:
                    # Check if the term is a common abbreviation
                    common_forms = AddressAbbreviation.objects.filter(
                        common_forms__icontains=term
                    )
                    if common_forms.exists():
                        # If the term is a common abbreviation, use the standard abbreviation for searching
                        standard_abbr = common_forms.first().standard_abbreviation
                        q_objects.append(Q(address_normalized__icontains=standard_abbr))
                    else:
                        # If the term is not a common abbreviation or state, search using the original term
                        q_objects.append(
                            Q(name__icontains=term)
                            | Q(address_normalized__icontains=term)
                            | Q(city__icontains=term)
                        )
            # Combine the Q objects using the & operator to perform an AND search
            query = q_objects.pop()
            for q in q_objects:
                query &= q
            queryset = queryset.filter(query)
        return queryset
