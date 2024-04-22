import re
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.contrib.postgres.search import TrigramSimilarity
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .utils import update_address_abbreviations
from .serializers import BuildingSerializer, CooperationSerializer
from .models import Building, AddressAbbreviation, Cooperation
from django.db.models import Q, F
from django.db.models.functions import Greatest
import pandas as pd

from .tasks import processBuildingDataBatch

import logging
logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("Realtor Buddy - Building Service")

def convertAndInsertBuildingData(request):
    df = pd.read_csv("/app/buildings_info.csv", low_memory=False)
    batch_size = 1000
    total_rows = len(df)
    # num_batches = (total_rows + batch_size - 1) // batch_size
    num_batches = 100

    tasks = []
    for batch in range(num_batches):
        start_index = batch * batch_size
        end_index = min((batch + 1) * batch_size, total_rows)

        rows = df.iloc[start_index:end_index].to_dict(orient="records")
        process = processBuildingDataBatch(rows, batch, num_batches)
        logger.info(
            f"Processing batch {batch+1} of {num_batches} with {len(rows)} rows"
        )

        tasks.append(
            {
                # "task_id": process.id,
                "batch": batch + 1,
                "start_index": start_index,
                "end_index": end_index,
            }
        )

    return JsonResponse({"tasks": tasks})

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

class CustomPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_query_param = "page"  # parameter for the page number in the query string
    page_size_query_param = (
        "page_size"  # parameter to override page size in the query string
    )
    max_page_size = 100  # maximum limit of the page size

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "count": self.page.paginator.count,
                "results": data,
            }
        )

def preprocess_search_query(query):
    # Using regular expressions to handle complex tokenization
    query = query.strip()
    query = re.sub(r"\s+", " ", query)  # Replace multiple whitespaces with a single space
    query = query.lower()
    ignore_words = {"at", "the", "on", "in", "by", "center"}
    words = re.split(r"\s+", query)  # Splitting on any whitespace
    filtered_words = [word for word in words if word.lower() not in ignore_words]
    return " ".join(filtered_words)

def is_address(query):
    # Using regular expressions to check if the query is an address
    address_pattern = r"\d+\s+\w+\s+\w+(\s+\w+)?(,\s+\w+)?"
    return bool(re.match(address_pattern, query))

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all().prefetch_related("cooperation")
    serializer_class = BuildingSerializer
    pagination_class = CustomPagination  # Use the custom pagination class

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
        if search:
            check_address = is_address(search)
            
            # Check for exact match first
            if check_address:
                logger.info("Searching for address")
                exact_match_queryset = queryset.filter(address__iexact=search)
                if exact_match_queryset.exists():
                    return exact_match_queryset
                
            else:
                logger.info("Searching for name")
                exact_match_queryset = queryset.filter(name__iexact=search)
                if exact_match_queryset.exists():
                    return exact_match_queryset
                
            # If no exact match, perform a broader search
            search_query = None
            search = preprocess_search_query(search) # Preprocess the search query if it not an exact match
            search_terms = re.split(r"\s+", search)  # Improved tokenization
            search_vectors = SearchVector("address", weight="A") if check_address else SearchVector("name", weight="A")
            # Building a combined search query for all terms using OR logic for broader matches
            for term in search_terms:
                if search_query:
                    search_query |= SearchQuery(term)
                else:
                    search_query = SearchQuery(term)

            # Apply the search vector and rank
            queryset = (
                queryset.annotate(
                    search_vector=search_vectors,
                    rank=SearchRank(F("search_vector"), search_query),
                )
                .filter(search_vector=search_query)
                .order_by("-rank", "name")
            )

        return queryset
