import datetime

import graphene
from bilby.models import BilbyJob
from django.conf import settings
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from gwauth.models import GWCloudUser
from jobserver.models import JobHistory

from db_search.utils.job_search import job_search


class UserNode(DjangoObjectType):
    class Meta:
        model = GWCloudUser
        fields = ("id", "username", "first_name", "last_name", "email", "is_ligo_user")


class BilbyJobNode(DjangoObjectType):
    class Meta:
        model = BilbyJob


class JobHistoryNode(DjangoObjectType):
    class Meta:
        model = JobHistory


class BilbyPublicJob(graphene.ObjectType):
    user = graphene.Field(UserNode)
    job = graphene.Field(BilbyJobNode)
    history = graphene.List(JobHistoryNode)


class Query(object):
    public_bilby_jobs = graphene.List(
        BilbyPublicJob,
        search=graphene.String(),
        time_range=graphene.String(),
        first=graphene.Int(),
        count=graphene.Int()
    )

    @login_required
    def resolve_public_bilby_jobs(self, info, **kwargs):
        # Get the search criteria
        search = kwargs.get("search", "")

        # Get the list of search terms
        search_terms = []
        for term in search.split(' '):
            # Remove any extraneous whitespace
            term = term.strip().lower()

            # If the term is valid, add it to the list of search terms
            if len(term):
                search_terms.append(term)

        # Calculate the end time for jobs
        time_range = kwargs.get("time_range", "1d")
        end_time = timezone.now()
        if time_range == "1d":
            end_time -= datetime.timedelta(days=1)
        elif time_range == "1w":
            end_time -= datetime.timedelta(weeks=1)
        elif time_range == "1m":
            end_time -= datetime.timedelta(days=31)
        elif time_range == "1y":
            end_time -= datetime.timedelta(days=365)
        else:
            end_time = datetime.datetime(year=1900, month=1, day=1)

        # Get the range
        first = kwargs.get("first", 0)
        count = kwargs.get("count", settings.GRAPHENE_RESULTS_LIMIT)

        # Limit the maximum number of results
        count = min(count, settings.GRAPHENE_RESULTS_LIMIT)

        # Perform the search
        jobs = job_search(search_terms, end_time, None, first, count)

        # Generate the results
        result = []

        for job in jobs:
            result.append(BilbyPublicJob(**job))

        # Done
        return result


class Mutation(graphene.ObjectType):
    pass
