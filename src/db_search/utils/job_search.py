from bilby.models import BilbyJob
from django.conf import settings
from gwauth.models import GWCloudUser
from jobserver.models import JobHistory

from db_search.status import JobStatus

sql_term_search = """
SELECT
    id
FROM
    {gwcloud_bilby}.bilby_bilbyjob
WHERE
    (
        user_id IN (
            SELECT
                id
            FROM
                {gwcloud_auth}.gwauth_gwclouduser
            WHERE
                first_name LIKE %(term)s
                OR last_name LIKE %(term)s
        )
        OR {gwcloud_bilby}.bilby_bilbyjob.name LIKE %(term)s
        OR {gwcloud_bilby}.bilby_bilbyjob.description LIKE %(term)s
    )
    AND job_id in (
        SELECT
            {gwcloud_jobcontroller}.jobserver_job.id
        FROM
            {gwcloud_jobcontroller}.jobserver_job
        INNER JOIN
            {gwcloud_jobcontroller}.jobserver_jobhistory ON
                ({gwcloud_jobcontroller}.jobserver_job.id = {gwcloud_jobcontroller}.jobserver_jobhistory.job_id)
        WHERE
            {gwcloud_jobcontroller}.jobserver_jobhistory.timestamp >= %(end_time)s
            AND (
                SELECT
                    {gwcloud_jobcontroller}.jobserver_jobhistory.state
                FROM
                    {gwcloud_jobcontroller}.jobserver_jobhistory
                WHERE
                    {gwcloud_jobcontroller}.jobserver_jobhistory.job_id = {gwcloud_jobcontroller}.jobserver_job.id
                ORDER BY {gwcloud_jobcontroller}.jobserver_jobhistory.timestamp DESC
                LIMIT 1
            ) in %(valid_states)s
    )
    AND {gwcloud_bilby}.bilby_bilbyjob.private = FALSE
"""


def job_search_single_term(term, end_time, valid_states):
    # We need to use the correct database names for testing
    if settings.TESTING:
        db_dict = \
            {
                'gwcloud_auth': settings.DATABASES['gwauth']['TEST']['NAME'],
                'gwcloud_bilby': settings.DATABASES['bilby']['TEST']['NAME'],
                'gwcloud_jobcontroller': settings.DATABASES['jobserver']['TEST']['NAME'],
            }
    else:
        db_dict = \
            {
                'gwcloud_auth': settings.DATABASES['gwauth']['NAME'],
                'gwcloud_bilby': settings.DATABASES['bilby']['NAME'],
                'gwcloud_jobcontroller': settings.DATABASES['jobserver']['NAME'],
            }

    sql_term_search_prepared = sql_term_search.format_map(db_dict)

    # Process the query for this term
    qs = BilbyJob.objects.using('bilby').raw(
        sql_term_search_prepared,
        {
            'term': f'%{term}%',
            'end_time': end_time,
            'valid_states': valid_states
        }
    )

    # Convert the query to a list of BilbyJob ID's and return
    return [job.id for job in qs]


def job_search(terms, end_time, order_by, first, count):
    """
    Searches for jobs by a list of terms

    :param terms: The list of terms to search on
    :param end_time: Jobs that have finished after this time
    :param order_by: Order by field
    :param first: Result start offset
    :param count: Number of results to return
    :return: A list of job "objects" that contain information about the bilby job
    """

    # Always include completed or running jobs
    states = [
        # A job is pending if it is currently waiting for a cluster to submit the job to
        # (ie, all available clusters are offline)
        JobStatus.PENDING,
        # A job is submitting if the job has been submitted but is waiting for the client to acknowledge it has received
        # the job submission command
        JobStatus.SUBMITTING,
        # A job is submitted if it is submitted on a cluster
        JobStatus.SUBMITTED,
        # A job is queued if it is in the queue on the cluster it is to run on
        JobStatus.QUEUED,
        # A job is running if it is currently running on the cluster it is to run on
        JobStatus.RUNNING,
        # A job is completed if it is finished running on the cluster without error
        JobStatus.COMPLETED
    ]

    # Prevent "use before define" warning
    jobs = None

    if len(terms):
        # Iterate over the terms
        for idx, term in enumerate(terms):
            if idx == 0:
                # If this is the first term, create the initial set of job ids
                jobs = set(job_search_single_term(term, end_time, states))
            else:
                # Otherwise intersect the set of job ids, such that the new term is contained in the results from the
                # previous search. (Every term must exist in each result)
                jobs = jobs.intersection(job_search_single_term(term, end_time, states))
    else:
        # If there are no terms, this query will be used which returns all bilby jobs
        jobs = job_search_single_term('', end_time, states)

    # Next we filter by range count
    jobs = BilbyJob.objects.using('bilby').filter(id__in=jobs)

    # Todo: Sort

    if first:
        jobs = jobs[first:]

    if count:
        jobs = jobs[:count]

    # Store the jobs in a dictionary by job id
    jobs = {job.job_id: job for job in jobs}

    # Get the list of user ids to fetch
    users = set()
    for job in jobs.values():
        users.add(job.user_id)

    # Get users and add them to a dictionary by user id
    users = GWCloudUser.objects.using('gwauth').filter(id__in=users)
    users = {user.id: user for user in users}

    # Get the job histories for the jobs found
    tmp_histories = JobHistory.objects.using('jobserver').filter(job_id__in=jobs.keys()).order_by('-timestamp')

    # Organise the job histories by job id
    histories = {job_id: [] for job_id in jobs.keys()}

    for history in tmp_histories:
        histories[history.job_id].append(history)

    # Compile the results
    result = []
    for job_id, job in jobs.items():
        result.append({
            'user': users[job.user_id],
            'history': histories[job_id],
            'job': job
        })

    return result
