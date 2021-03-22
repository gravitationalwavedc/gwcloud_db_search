import datetime

import graphene
from django.conf import settings
from django.utils import timezone
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from gwauth.models import GWCloudUser
from jobserver.models import JobHistory
from bilby.models import BilbyJob
from viterbi.models import ViterbiJob

from db_search.utils.job_search import job_search


class UserNode(DjangoObjectType):
    class Meta:
        model = GWCloudUser
        fields = ("id", "username", "first_name", "last_name", "email", "is_ligo_user")


class JobHistoryNode(DjangoObjectType):
    class Meta:
        model = JobHistory


class BilbyJobNode(DjangoObjectType):
    class Meta:
        model = BilbyJob


class BilbyPublicJob(graphene.ObjectType):
    user = graphene.Field(UserNode)
    job = graphene.Field(BilbyJobNode)
    history = graphene.List(JobHistoryNode)


class ViterbiJobNode(DjangoObjectType):
    class Meta:
        model = ViterbiJob


class ViterbiPublicJob(graphene.ObjectType):
    user = graphene.Field(UserNode)
    job = graphene.Field(ViterbiJobNode)
    history = graphene.List(JobHistoryNode)


search_kwargs = dict(
    search=graphene.String(),
    time_range=graphene.String(),
    first=graphene.Int(),
    count=graphene.Int(),
    exclude_ligo_jobs=graphene.Boolean()
)


class Query(object):
    public_bilby_jobs = graphene.List(
        BilbyPublicJob,
        search_kwargs
    )

    public_viterbi_jobs = graphene.List(
        ViterbiPublicJob,
        search_kwargs
    )

    @staticmethod
    def perform_search(klass, application, info, **kwargs):
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

        # Check if we should exclude LIGO jobs or not
        exclude_ligo_jobs = kwargs.get("exclude_ligo_jobs", True)

        # Perform the search
        jobs = job_search(application, search_terms, end_time, None, first, count, exclude_ligo_jobs)

        # Generate the results
        return [klass(**job) for job in jobs]

    @login_required
    def resolve_public_bilby_jobs(self, info, **kwargs):
        return Query.perform_search(BilbyPublicJob, 'bilby', info, **kwargs)

    @login_required
    def resolve_public_viterbi_jobs(self, info, **kwargs):
        return Query.perform_search(ViterbiPublicJob, 'viterbi', info, **kwargs)


class Mutation(graphene.ObjectType):
    pass
