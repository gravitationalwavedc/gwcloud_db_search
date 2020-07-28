import graphene
from graphene import relay


class BilbyPublicJobNode(graphene.ObjectType):
    user = graphene.String()
    name = graphene.String()
    job_status = graphene.String()
    description = graphene.String()
    timestamp = graphene.String()
    id = graphene.ID()


class BilbyPublicJobConnection(relay.Connection):
    class Meta:
        node = BilbyPublicJobNode


class Query(object):
    public_bilby_jobs = relay.ConnectionField(
        BilbyPublicJobConnection,
        order_by=graphene.String(),
        search=graphene.String(),
        time_range=graphene.String()
    )

    # @login_required
    def resolve_public_bilby_jobs(self, info, **kwargs):
        return []
        # Get the search criteria
        # search = kwargs.get("search", "")
        #
        # # Get the list of search terms
        # search_terms = []
        # for term in search.split(' '):
        #     # Remove any extranious whitespace
        #     term = term.strip().lower()
        #
        #     # If the term is valid, add it to the list of search terms
        #     if len(term):
        #         search_terms.append(term)
        #
        # # If there are search terms
        # if len(search_terms):
        #     # First look up a list of users
        #     _, terms = request_filter_users(" ".join(search_terms), info.context.user.user_id)
        #
        #     # Collate the user id's to search for jobs on
        #     user_ids = []
        #     for term in terms:
        #         for user in term['users']:
        #             user_ids.append(user['userId'])
        #
        #     jobs = BilbyJob.objects.filter(user_id__in=user_ids)
        # else:
        #     jobs = BilbyJob.objects.all()
        #
        # # Make sure every job has a valid job id and is public
        # jobs = jobs.filter(job_id__isnull=False, private=False)
        #
        # # Calculate the end time for jobs
        # time_range = kwargs.get("time_range", "1d")
        # end_time = datetime.datetime.now()
        # if time_range == "1d":
        #     end_time -= datetime.timedelta(days=1)
        # elif time_range == "1w":
        #     end_time -= datetime.timedelta(weeks=1)
        # elif time_range == "1m":
        #     end_time -= datetime.timedelta(days=31)
        # elif time_range == "1y":
        #     end_time -= datetime.timedelta(days=365)
        # else:
        #     end_time = None
        #
        # # Get job details from the job controller
        # _, jc_jobs = request_job_filter(
        #     info.context.user.user_id,
        #     ids=[j['job_id'] for j in jobs.values("job_id").distinct()],
        #     end_time_gt=end_time
        # )
        #
        # # Make sure that the result is an array
        # jc_jobs = jc_jobs or []
        #
        # # Get the user id's that match any of the terms
        # user_ids = set([j['user'] for j in jc_jobs])
        #
        # # Get the user id's from the list of jobs
        # _, user_details = request_lookup_users(user_ids, info.context.user.user_id)
        #
        # def user_from_id(user_id):
        #     for u in user_details:
        #         if u['userId'] == user_id:
        #             return u
        #
        #     return "Unknown User"
        #
        # # Match user and job details to the job controller results
        # valid_jobs = []
        # for job in jc_jobs:
        #     try:
        #         job["user"] = user_from_id(job["user"])
        #         job["job"] = jobs.get(job_id=job["id"])
        #
        #         job_status, job_status_str, timestamp = derive_job_status(job["history"])
        #         job["status"] = job_status_str
        #         job["status_int"] = job_status
        #         job["timestamp"] = timestamp.strftime("%d/%m/%Y, %H:%M:%S")
        #
        #         valid_jobs.append(job)
        #     except Exception:
        #         pass
        #
        # jc_jobs = valid_jobs
        #
        # def user_name_from_id(user_id):
        #     for u in user_details:
        #         if u['userId'] == user_id:
        #             return f"{u['firstName']} {u['lastName']}"
        #
        #     return "Unknown User"
        #
        # # Now do the search
        # matched_jobs = []
        #
        # # Iterate over each job
        # for job in jc_jobs:
        #     # Iterate over each term and make sure the term exists in the record
        #     valid = True
        #
        #     valid_status = [
        #         JobStatus.PENDING,
        #         JobStatus.SUBMITTING,
        #         JobStatus.SUBMITTED,
        #         JobStatus.QUEUED,
        #         JobStatus.RUNNING,
        #         JobStatus.COMPLETED
        #     ]
        #
        #     status_valid = True
        #
        #     if not len(search_terms) and job["status_int"] not in valid_status:
        #         status_valid = False
        #
        #     if len(search_terms) and job["status_int"] not in valid_status:
        #         status_valid = False
        #
        #     status_valid_terms = []
        #     if not status_valid:
        #         # Check if any search terms match the job status
        #         for term in search_terms:
        #             if term in job["status"].lower():
        #                 status_valid = True
        #                 status_valid_terms.append(term)
        #                 break
        #
        #     for term in search_terms:
        #         if not valid:
        #             break
        #
        #         # Match username, first name and last name
        #         if term in job["user"]["username"].lower():
        #             continue
        #         if term in job["user"]["firstName"].lower():
        #             continue
        #         if term in job["user"]["lastName"].lower():
        #             continue
        #
        #         # Match job name
        #         if term in job["job"].name.lower():
        #             continue
        #
        #         # Match description
        #         if term in job["job"].description.lower():
        #             continue
        #
        #         if term in status_valid_terms:
        #             continue
        #
        #         valid = False
        #
        #     if valid and status_valid:
        #         matched_jobs.append(
        #             BilbyPublicJobNode(
        #                 user=user_name_from_id(job["user"]["userId"]),
        #                 name=job["job"].name,
        #                 job_status=job["status"],
        #                 description=job["job"].description,
        #                 timestamp=job["timestamp"],
        #                 id=to_global_id("BilbyJobNode", job["job"].id)
        #             )
        #         )
        #
        # return matched_jobs


class Mutation(graphene.ObjectType):
    pass
