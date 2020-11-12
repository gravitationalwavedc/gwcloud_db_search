from django.conf import settings
from gwauth.models import GWCloudUser
from jobserver.models import JobHistory
from bilby.models import BilbyJob
from viterbi.models import ViterbiJob

from db_search.status import JobStatus

sql_term_search = """
SELECT
    id
FROM
    {job_database}
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
        OR {job_database}.name LIKE %(term)s
        OR {job_database}.description LIKE %(term)s
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
            AND application = %(application)s
    )
    AND {job_database}.private = FALSE
"""


def job_search_single_term(application, job_klass, term, end_time, valid_states):
    """
    Performs a database search for all jobs matching:-
        * the specified single word term
        * between now until end time
        * the specified job states

    :param application: The application to perform the search on, ie, "viterbi" or "bilby"
    :param job_klass: The class representing the main job class for the provided application, ie, BilbyJob or ViterbiJob
    :param term: The single word term to filter on
    :param end_time: Jobs that have finished or updated up until this time will be considered
    :param valid_states: An array of job states to filter on

    :return: A list of job IDs representing the matched jobs
    """
    # We need to use the correct database names for testing
    if settings.TESTING:
        db_dict = \
            {
                'gwcloud_auth': settings.DATABASES['gwauth']['TEST']['NAME'],
                'gwcloud_jobcontroller': settings.DATABASES['jobserver']['TEST']['NAME'],
            }

        if application == 'bilby':
            db_dict['job_database'] = settings.DATABASES['bilby']['TEST']['NAME'] + '.bilby_bilbyjob'
        elif application == 'viterbi':
            db_dict['job_database'] = settings.DATABASES['viterbi']['TEST']['NAME'] + '.viterbi_viterbijob'
    else:
        db_dict = \
            {
                'gwcloud_auth': settings.DATABASES['gwauth']['NAME'],
                'gwcloud_jobcontroller': settings.DATABASES['jobserver']['NAME'],
            }

        if application == 'bilby':
            db_dict['job_database'] = settings.DATABASES['bilby']['NAME'] + '.bilby_bilbyjob'
        elif application == 'viterbi':
            db_dict['job_database'] = settings.DATABASES['viterbi']['NAME'] + '.viterbi_viterbijob'

    # Format the database query
    sql_term_search_prepared = sql_term_search.format_map(db_dict)

    # Process the query for this term
    qs = job_klass.objects.using(application).raw(
        sql_term_search_prepared,
        {
            'term': f'%{term}%',
            'end_time': end_time,
            'valid_states': valid_states,
            'application': application
        }
    )

    # Convert the query to a list of Job IDs and return
    return [job.id for job in qs]


def job_search(application, terms, end_time, order_by, first, count):
    """
    Searches for jobs by a list of terms

    :param application: The application to perform the search on, ie, "viterbi" or "bilby"
    :param terms: The list of terms to search on
    :param end_time: Jobs that have finished after this time
    :param order_by: Order by field
    :param first: Result start offset
    :param count: Number of results to return

    :return: A list of job "objects" that contain information about the matched jobs
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

    # Get the job class
    job_klass = None
    if application == 'bilby':
        job_klass = BilbyJob
    elif application == 'viterbi':
        job_klass = ViterbiJob

    # Prevent "use before define" warning
    jobs = None

    if len(terms):
        # Iterate over the terms
        for idx, term in enumerate(terms):
            if idx == 0:
                # If this is the first term, create the initial set of job ids
                jobs = set(job_search_single_term(application, job_klass, term, end_time, states))
            else:
                # Otherwise intersect the set of job ids, such that the new term is contained in the results from the
                # previous search. (Every term must exist in each result)
                jobs = jobs.intersection(job_search_single_term(application, job_klass, term, end_time, states))
    else:
        # If there are no terms, this query will be used which returns all jobs
        jobs = job_search_single_term(application, job_klass, '', end_time, states)

    # Next we filter by range count
    jobs = job_klass.objects.using(application).filter(id__in=jobs)

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
