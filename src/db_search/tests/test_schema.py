from bilby.models import BilbyJob
from bilby.tests.testcases import BilbyTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from gwauth.models import GWCloudUser
from jobserver.models import JobHistory, Job

from db_search.status import JobStatus

User = get_user_model()


class TestQueries(BilbyTestCase):
    databases = '__all__'

    def setUp(self):
        self.maxDiff = 999999

        # Clean everything up first just in case - because we are unable to use TransactionTestCase which would normally
        # manage this for us
        GWCloudUser.objects.using('gwauth').all().delete()
        Job.objects.using('jobserver').all().delete()
        JobHistory.objects.using('jobserver').all().delete()
        BilbyJob.objects.using('bilby').all().delete()

        # Insert users
        self.user_1 = GWCloudUser.objects.using('gwauth').create(
            username='user1_magenta',
            first_name='User',
            last_name='One'
        )

        self.user_2 = GWCloudUser.objects.using('gwauth').create(
            username='user2_yellow',
            first_name='Another',
            last_name='Two'
        )

        # Insert jobs

        # Completed Job
        self.job_controller_job_completed = Job.objects.using('jobserver').create(
            user=self.user_1.id,
            cluster="test_cluster",
            bundle="test_bundle"
        )

        self.job_controller_job_completed_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_completed,
            what='_job_completion_',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )

        self.bilby_job_completed = BilbyJob.objects.using('bilby').create(
            user_id=self.job_controller_job_completed.user,
            job_id=self.job_controller_job_completed.id,
            name="test_job",
            description="my potato job is brown",
            private=False
        )

        # Completed job 2
        self.job_controller_job_completed2 = Job.objects.using('jobserver').create(
            user=self.user_2.id,
            cluster="test_cluster",
            bundle="test_bundle"
        )

        self.job_controller_job_completed2_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_completed2,
            what='submit',
            state=JobStatus.QUEUED,
            timestamp=timezone.now()
        )
        self.job_controller_job_completed2_history2 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_completed2,
            what='submit',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )
        self.job_controller_job_completed2_history3 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_completed2,
            what='_job_completion_',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )

        self.bilby_job_completed2 = BilbyJob.objects.using('bilby').create(
            user_id=self.job_controller_job_completed2.user,
            job_id=self.job_controller_job_completed2.id,
            name="test_job_purple",
            description="this job is actually cyan",
            private=False
        )

        # Incomplete job
        self.job_controller_job_incomplete = Job.objects.using('jobserver').create(
            user=self.user_2.id,
            cluster="test_cluster",
            bundle="test_bundle"
        )

        self.job_controller_job_incomplete_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_incomplete,
            what='submit',
            state=JobStatus.RUNNING,
            timestamp=timezone.now()
        )

        self.bilby_job_incomplete = BilbyJob.objects.using('bilby').create(
            user_id=self.job_controller_job_incomplete.user,
            job_id=self.job_controller_job_incomplete.id,
            name="test_job_incomplete",
            description="my potato job is violet",
            private=False
        )

        # Errored Job
        self.job_controller_job_error = Job.objects.using('jobserver').create(
            user=self.user_1.id,
            cluster="test_cluster",
            bundle="test_bundle"
        )

        self.job_controller_job_error_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error,
            what='submit',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )
        self.job_controller_job_error_history2 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error,
            what='jid0',
            state=JobStatus.ERROR,
            timestamp=timezone.now()
        )
        self.job_controller_job_error_history3 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error,
            what='_job_completion_',
            state=JobStatus.ERROR,
            timestamp=timezone.now()
        )

        self.bilby_job_error = BilbyJob.objects.using('bilby').create(
            user_id=self.job_controller_job_error.user,
            job_id=self.job_controller_job_error.id,
            name="test_job_error",
            description="This job is also violet - but is an error so should never show up",
            private=False
        )

        # Errored Job
        self.job_controller_job_error2 = Job.objects.using('jobserver').create(
            user=self.user_2.id,
            cluster="test_cluster",
            bundle="test_bundle"
        )

        self.job_controller_job_error2_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error2,
            what='submit',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )
        self.job_controller_job_error2_history2 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error2,
            what='jid0',
            state=JobStatus.QUEUED,
            timestamp=timezone.now()
        )
        self.job_controller_job_error2_history3 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error2,
            what='jid0',
            state=JobStatus.RUNNING,
            timestamp=timezone.now()
        )
        self.job_controller_job_error2_history4 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error2,
            what='jid0',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )
        self.job_controller_job_error2_history5 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error2,
            what='jid1',
            state=JobStatus.RUNNING,
            timestamp=timezone.now()
        )
        self.job_controller_job_error2_history6 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error2,
            what='jid1',
            state=JobStatus.WALL_TIME_EXCEEDED,
            timestamp=timezone.now()
        )
        self.job_controller_job_error2_history7 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_error2,
            what='_job_completion_',
            state=JobStatus.WALL_TIME_EXCEEDED,
            timestamp=timezone.now()
        )

        self.bilby_job_error = BilbyJob.objects.using('bilby').create(
            user_id=self.job_controller_job_error.user,
            job_id=self.job_controller_job_error.id,
            name="test_job_error_GWOSC",
            description="my potato job is another errored job but let's call this one magenta",
            private=False
        )

    def test_no_terms(self):
        # response = self.client.execute(
        #     f"""
        #
        #     """
        # )
        pass

    def test_single_term(self):
        pass

    def test_multiple_terms(self):
        pass
