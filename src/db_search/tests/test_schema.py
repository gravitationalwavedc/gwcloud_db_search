import datetime

import graphene
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from gwauth.models import GWCloudUser
from jobserver.models import JobHistory, Job
from bilbyui.models import BilbyJob
from viterbi.models import ViterbiJob

from db_search.status import JobStatus
from db_search.tests.testcases import CustomJwtTestCase

User = get_user_model()


@override_settings(TESTING=True)
class TestQueriesCustom(CustomJwtTestCase):
    databases = '__all__'

    def setUp(self):
        self.maxDiff = 999999

        # Clean everything up first just in case - because we are unable to use TransactionTestCase which would normally
        # manage this for us
        GWCloudUser.objects.using('gwauth').all().delete()
        Job.objects.using('jobserver').all().delete()
        JobHistory.objects.using('jobserver').all().delete()
        BilbyJob.objects.using('bilbyui').all().delete()
        ViterbiJob.objects.using('viterbi').all().delete()

        # Insert users
        self.user_1 = GWCloudUser.objects.using('gwauth').create(
            email='user1@example.com',
            username='user1_magenta',
            first_name='User magenta',
            last_name='One'
        )

        self.client.authenticate(self.user_1)

        self.user_2 = GWCloudUser.objects.using('gwauth').create(
            email='user2@example.com',
            username='user2_yellow',
            first_name='Another User',
            last_name='Two yellow'
        )

        # Insert jobs

        # Completed Job
        self.job_controller_job_completed = Job.objects.using('jobserver').create(
            user=self.user_1.id,
            cluster="test_cluster",
            bundle="test_bundle",
            application='bilbyui'
        )

        self.job_controller_job_completed_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_completed,
            what='_job_completion_',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )

        self.bilby_job_completed = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_completed.user,
            job_controller_id=self.job_controller_job_completed.id,
            name="test_job",
            description="my potato job is brown",
            private=False,
            is_ligo_job=True
        )

        self.bilby_job_completed_result = {
            'user': {
                'id': str(self.user_1.id),
                'username': 'user1_magenta',
                'firstName': 'User magenta',
                'lastName': 'One',
                'email': 'user1@example.com',
                'isLigoUser': False
            },
            'job': {
                'id': str(self.bilby_job_completed.id),
                'userId': self.bilby_job_completed.user_id,
                'name': 'test_job',
                'description': 'my potato job is brown',
                'creationTime': graphene.DateTime().serialize(self.bilby_job_completed.creation_time),
                'lastUpdated': graphene.DateTime().serialize(self.bilby_job_completed.last_updated),
                'private': False,
                'jobControllerId': self.bilby_job_completed.job_controller_id
            },
            'history': [{
                'id': str(self.job_controller_job_completed_history1.id),
                'timestamp': graphene.DateTime().serialize(self.job_controller_job_completed_history1.timestamp),
                'what': '_job_completion_',
                'state': 500,
                'details': ''
            }]
        }

        # Completed job 2
        self.job_controller_job_completed2 = Job.objects.using('jobserver').create(
            user=self.user_2.id,
            cluster="test_cluster",
            bundle="test_bundle",
            application='bilbyui'
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

        self.bilby_job_completed2 = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_completed2.user,
            job_controller_id=self.job_controller_job_completed2.id,
            name="test_job_purple",
            description="this job is actually cyan",
            private=False
        )

        self.bilby_job_completed2_result = {
            'user': {
                'id': str(self.user_2.id),
                'username': 'user2_yellow',
                'firstName': 'Another User',
                'lastName': 'Two yellow',
                'email': 'user2@example.com',
                'isLigoUser': False
            },
            'job': {
                'id': str(self.bilby_job_completed2.id),
                'userId': self.bilby_job_completed2.user_id,
                'name': 'test_job_purple',
                'description': 'this job is actually cyan',
                'creationTime': graphene.DateTime().serialize(self.bilby_job_completed2.creation_time),
                'lastUpdated': graphene.DateTime().serialize(self.bilby_job_completed2.last_updated),
                'private': False,
                'jobControllerId': self.bilby_job_completed2.job_controller_id
            },
            'history': [{
                'id': str(self.job_controller_job_completed2_history3.id),
                'timestamp': graphene.DateTime().serialize(self.job_controller_job_completed2_history3.timestamp),
                'what': '_job_completion_',
                'state': 500,
                'details': ''
            }, {
                'id': str(self.job_controller_job_completed2_history2.id),
                'timestamp': graphene.DateTime().serialize(self.job_controller_job_completed2_history2.timestamp),
                'what': 'submit',
                'state': 500,
                'details': ''
            }, {
                'id': str(self.job_controller_job_completed2_history1.id),
                'timestamp': graphene.DateTime().serialize(self.job_controller_job_completed2_history1.timestamp),
                'what': 'submit',
                'state': 40,
                'details': ''
            }]
        }

        # Incomplete job
        self.job_controller_job_incomplete = Job.objects.using('jobserver').create(
            user=self.user_2.id,
            cluster="test_cluster",
            bundle="test_bundle",
            application='bilbyui'
        )

        self.job_controller_job_incomplete_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_incomplete,
            what='submit',
            state=JobStatus.RUNNING,
            timestamp=timezone.now()
        )

        self.bilby_job_incomplete = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_incomplete.user,
            job_controller_id=self.job_controller_job_incomplete.id,
            name="test_job_incomplete",
            description="my potato job is violet",
            private=False
        )

        self.bilby_job_incomplete_result = {
            'user': {
                'id': str(self.user_2.id),
                'username': 'user2_yellow',
                'firstName': 'Another User',
                'lastName': 'Two yellow',
                'email': 'user2@example.com',
                'isLigoUser': False
            },
            'job': {
                'id': str(self.bilby_job_incomplete.id),
                'userId': self.user_2.id,
                'name': 'test_job_incomplete',
                'description': 'my potato job is violet',
                'creationTime': graphene.DateTime().serialize(self.bilby_job_incomplete.creation_time),
                'lastUpdated': graphene.DateTime().serialize(self.bilby_job_incomplete.last_updated),
                'private': False,
                'jobControllerId': self.bilby_job_incomplete.job_controller_id
            },
            'history': [{
                'id': str(self.job_controller_job_incomplete_history1.id),
                'timestamp': graphene.DateTime().serialize(self.job_controller_job_incomplete_history1.timestamp),
                'what': 'submit',
                'state': 50,
                'details': ''
            }]
        }

        # Errored Job
        self.job_controller_job_error = Job.objects.using('jobserver').create(
            user=self.user_1.id,
            cluster="test_cluster",
            bundle="test_bundle",
            application='bilbyui'
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

        self.bilby_job_error = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_error.user,
            job_controller_id=self.job_controller_job_error.id,
            name="test_job_error",
            description="This job is also violet - but is an error so should never show up",
            private=False
        )

        # Errored Job
        self.job_controller_job_error2 = Job.objects.using('jobserver').create(
            user=self.user_2.id,
            cluster="test_cluster",
            bundle="test_bundle",
            application='bilbyui'
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

        self.bilby_job_error = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_error.user,
            job_controller_id=self.job_controller_job_error.id,
            name="test_job_error_GWOSC",
            description="my potato job is another errored job but let's call this one magenta",
            private=False
        )

        # Completed Job (In the past)
        self.job_controller_job_completed_old = Job.objects.using('jobserver').create(
            user=self.user_2.id,
            cluster="test_cluster",
            bundle="test_bundle",
            application='bilbyui'
        )

        self.job_controller_job_completed_old_history1 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_completed_old,
            what='_job_completion_',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now() - datetime.timedelta(days=366)
        )

        self.bilby_job_completed_old = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_completed_old.user,
            job_controller_id=self.job_controller_job_completed_old.id,
            name="test_job_orange",
            description="my potato job is orange",
            private=False
        )

        self.bilby_job_completed_result_old = None
        self.update_old_result()

        self.job_controller_job_completed_viterbi = Job.objects.using('jobserver').create(
            user=self.user_1.id,
            cluster="test_cluster",
            bundle="test_bundle",
            application='viterbi'
        )

        self.job_controller_job_completed_history1_viterbi = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_completed_viterbi,
            what='_job_completion_',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )

        self.job_completed_viterbi = ViterbiJob.objects.using('viterbi').create(
            user_id=self.job_controller_job_completed_viterbi.user,
            job_controller_id=self.job_controller_job_completed_viterbi.id,
            name="test_job_viterbi",
            description="my potato job is brown_viterbi",
            private=False
        )

        self.job_completed_result_viterbi = {
            'user': {
                'id': str(self.user_1.id),
                'username': 'user1_magenta',
                'firstName': 'User magenta',
                'lastName': 'One',
                'email': 'user1@example.com',
                'isLigoUser': False
            },
            'job': {
                'id': str(self.job_completed_viterbi.id),
                'userId': self.job_completed_viterbi.user_id,
                'name': 'test_job_viterbi',
                'description': 'my potato job is brown_viterbi',
                'creationTime': graphene.DateTime().serialize(self.job_completed_viterbi.creation_time),
                'lastUpdated': graphene.DateTime().serialize(self.job_completed_viterbi.last_updated),
                'private': False,
                'jobControllerId': self.job_completed_viterbi.job_controller_id
            },
            'history': [{
                'id': str(self.job_controller_job_completed_history1_viterbi.id),
                'timestamp': graphene.DateTime().serialize(
                    self.job_controller_job_completed_history1_viterbi.timestamp
                ),
                'what': '_job_completion_',
                'state': 500,
                'details': ''
            }]
        }

    def update_old_result(self):
        self.bilby_job_completed_result_old = {
            'user': {
                'id': str(self.user_2.id),
                'username': 'user2_yellow',
                'firstName': 'Another User',
                'lastName': 'Two yellow',
                'email': 'user2@example.com',
                'isLigoUser': False
            },
            'job': {
                'id': str(self.bilby_job_completed_old.id),
                'userId': self.bilby_job_completed_old.user_id,
                'name': 'test_job_orange',
                'description': 'my potato job is orange',
                'creationTime': graphene.DateTime().serialize(self.bilby_job_completed_old.creation_time),
                'lastUpdated': graphene.DateTime().serialize(self.bilby_job_completed_old.last_updated),
                'private': False,
                'jobControllerId': self.bilby_job_completed_old.job_controller_id
            },
            'history': [{
                'id': str(self.job_controller_job_completed_old_history1.id),
                'timestamp': graphene.DateTime().serialize(self.job_controller_job_completed_old_history1.timestamp),
                'what': '_job_completion_',
                'state': 500,
                'details': ''
            }]
        }

    def test_time_ranges(self):
        def run_default(expected):
            response = self.client.execute(
                """
                    query {
                      publicBilbyJobs(excludeLigoJobs: false) {
                        user {
                          id
                          username
                          firstName
                          lastName
                          email
                          isLigoUser
                        }
                        job {
                          id
                          userId
                          name
                          description
                          creationTime
                          lastUpdated
                          private
                          jobControllerId
                        }
                        history {
                          id
                          timestamp
                          what
                          state
                          details
                        }
                      }
                    }
                """
            )

            self.assertDictEqual(
                expected, response.data, "publicBilbyJobs query returned unexpected data."
            )

        # Test default time (1d)
        run_default({
            'publicBilbyJobs': [
                self.bilby_job_incomplete_result,
                self.bilby_job_completed2_result,
                self.bilby_job_completed_result
            ]
        })

        # Check default is really 1 day
        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=1) - datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_default({
            'publicBilbyJobs': [
                self.bilby_job_incomplete_result,
                self.bilby_job_completed2_result,
                self.bilby_job_completed_result,
            ]
        })

        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=1) + datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_default({
            'publicBilbyJobs': [
                self.bilby_job_completed_result_old,
                self.bilby_job_incomplete_result,
                self.bilby_job_completed2_result,
                self.bilby_job_completed_result
            ]
        })

        def run_time_range(_range, expected):
            response = self.client.execute(
                f"""
                    query {{
                      publicBilbyJobs (timeRange: "{_range}", excludeLigoJobs: false) {{
                        user {{
                          id
                          username
                          firstName
                          lastName
                          email
                          isLigoUser
                        }}
                        job {{
                          id
                          userId
                          name
                          description
                          creationTime
                          lastUpdated
                          private
                          jobControllerId
                        }}
                        history {{
                          id
                          timestamp
                          what
                          state
                          details
                        }}
                      }}
                    }}
                """
            )

            self.assertDictEqual(
                expected, response.data, "publicBilbyJobs query returned unexpected data."
            )

        # Test 1d
        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=1) - datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1d',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=1) + datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1d',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed_result_old,
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        # Test 1w
        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(weeks=1) - datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1w',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(weeks=1) + datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1w',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed_result_old,
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        # Test 1m
        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=31) - datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1m',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=31) + datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1m',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed_result_old,
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        # Test 1y
        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=365) - datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1y',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=365) + datetime.timedelta(seconds=5)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '1y',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed_result_old,
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        # Test all time
        self.job_controller_job_completed_old_history1.timestamp = \
            timezone.now() - datetime.timedelta(days=10000)
        self.job_controller_job_completed_old_history1.save()

        self.update_old_result()

        run_time_range(
            '',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed_result_old,
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

    def run_terms_bilby(self, terms, expected):
        response = self.client.execute(
            f"""
                query {{
                  publicBilbyJobs (search: "{terms}", excludeLigoJobs: false) {{
                    user {{
                      id
                      username
                      firstName
                      lastName
                      email
                      isLigoUser
                    }}
                    job {{
                      id
                      userId
                      name
                      description
                      creationTime
                      lastUpdated
                      private
                      jobControllerId
                    }}
                    history {{
                      id
                      timestamp
                      what
                      state
                      details
                    }}
                  }}
                }}
            """
        )

        self.assertDictEqual(
            expected, response.data, "publicBilbyJobs query returned unexpected data."
        )

    def run_terms_viterbi(self, terms, expected):
        response = self.client.execute(
            f"""
                query {{
                  publicViterbiJobs (search: "{terms}") {{
                    user {{
                      id
                      username
                      firstName
                      lastName
                      email
                      isLigoUser
                    }}
                    job {{
                      id
                      userId
                      name
                      description
                      creationTime
                      lastUpdated
                      private
                      jobControllerId
                    }}
                    history {{
                      id
                      timestamp
                      what
                      state
                      details
                    }}
                  }}
                }}
            """
        )

        self.assertDictEqual(
            expected, response.data, "publicViterbiJobs query returned unexpected data."
        )

    def test_single_term(self):
        self.run_terms_bilby(
            'magenta',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed_result
                ]
            }
        )

        self.run_terms_bilby(
            'yellow',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result
                ]
            }
        )

        self.run_terms_bilby(
            'cyan',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed2_result
                ]
            }
        )

        self.run_terms_bilby(
            'user',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result,
                ]
            }
        )

        self.run_terms_viterbi(
            'magenta',
            {
                'publicViterbiJobs': [
                    self.job_completed_result_viterbi
                ]
            }
        )

    def test_multiple_terms(self):
        self.run_terms_bilby(
            'user yellow',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result
                ]
            }
        )

        self.run_terms_bilby(
            'user yellow',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result
                ]
            }
        )

        self.run_terms_bilby(
            'user yellow test',
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result
                ]
            }
        )

        self.run_terms_bilby(
            'user yellow test purple',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed2_result
                ]
            }
        )

        self.run_terms_bilby(
            'user yellow test purple cyan',
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed2_result
                ]
            }
        )

        self.run_terms_bilby(
            'user yellow test purple cyan magenta',
            {
                'publicBilbyJobs': [
                ]
            }
        )

    def test_range(self):
        def run_range_first(first, expected):
            response = self.client.execute(
                f"""
                    query {{
                      publicBilbyJobs (first: {first}, excludeLigoJobs: false) {{
                        user {{
                          id
                          username
                          firstName
                          lastName
                          email
                          isLigoUser
                        }}
                        job {{
                          id
                          userId
                          name
                          description
                          creationTime
                          lastUpdated
                          private
                          jobControllerId
                        }}
                        history {{
                          id
                          timestamp
                          what
                          state
                          details
                        }}
                      }}
                    }}
                """
            )

            self.assertDictEqual(
                expected, response.data, "publicBilbyJobs query returned unexpected data."
            )

        def run_range_count(count, expected):
            response = self.client.execute(
                f"""
                    query {{
                      publicBilbyJobs (count: {count}, excludeLigoJobs: false) {{
                        user {{
                          id
                          username
                          firstName
                          lastName
                          email
                          isLigoUser
                        }}
                        job {{
                          id
                          userId
                          name
                          description
                          creationTime
                          lastUpdated
                          private
                          jobControllerId
                        }}
                        history {{
                          id
                          timestamp
                          what
                          state
                          details
                        }}
                      }}
                    }}
                """
            )

            self.assertDictEqual(
                expected, response.data, "publicBilbyJobs query returned unexpected data."
            )

        def run_range(first, count, expected):
            response = self.client.execute(
                f"""
                    query {{
                      publicBilbyJobs (first: {first}, count: {count}, excludeLigoJobs: false) {{
                        user {{
                          id
                          username
                          firstName
                          lastName
                          email
                          isLigoUser
                        }}
                        job {{
                          id
                          userId
                          name
                          description
                          creationTime
                          lastUpdated
                          private
                          jobControllerId
                        }}
                        history {{
                          id
                          timestamp
                          what
                          state
                          details
                        }}
                      }}
                    }}
                """
            )

            self.assertDictEqual(
                expected, response.data, "publicBilbyJobs query returned unexpected data."
            )

        run_range_first(
            1,
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        run_range_first(
            1000,
            {
                'publicBilbyJobs': [
                ]
            }
        )

        run_range_count(
            1,
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                ]
            }
        )

        run_range_count(
            1000,
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

        run_range(
            1, 1,
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed2_result,
                ]
            }
        )

        run_range(
            1, 1000,
            {
                'publicBilbyJobs': [
                    self.bilby_job_completed2_result,
                    self.bilby_job_completed_result
                ]
            }
        )

    def test_exclude_ligo(self):
        def run_bilby_exclude_ligo(expected):
            response = self.client.execute(
                """
                    query {
                      publicBilbyJobs (excludeLigoJobs: true) {
                        user {
                          id
                          username
                          firstName
                          lastName
                          email
                          isLigoUser
                        }
                        job {
                          id
                          userId
                          name
                          description
                          creationTime
                          lastUpdated
                          private
                          jobControllerId
                        }
                        history {
                          id
                          timestamp
                          what
                          state
                          details
                        }
                      }
                    }
                """
            )

            self.assertDictEqual(
                expected, response.data, "publicBilbyJobs query returned unexpected data."
            )

        run_bilby_exclude_ligo(
            {
                'publicBilbyJobs': [
                    self.bilby_job_incomplete_result,
                    self.bilby_job_completed2_result
                ]
            }
        )

    def test_result_ordering(self):
        mutation = """
            query {
                publicBilbyJobs (excludeLigoJobs: false) {
                    user {
                        id
                        username
                        firstName
                        lastName
                        email
                        isLigoUser
                    }
                    job {
                        id
                        userId
                        name
                        description
                        creationTime
                        lastUpdated
                        private
                        jobControllerId
                    }
                    history {
                        id
                        timestamp
                        what
                        state
                        details
                    }
                }
            }
            """

        def fetch_jobs(expected):
            response = self.client.execute(mutation)

            self.assertDictEqual(
                expected, response.data, "publicBilbyJobs query returned unexpected data."
            )

        # First check that the default job order is correct
        fetch_jobs({
            'publicBilbyJobs': [
                self.bilby_job_incomplete_result,
                self.bilby_job_completed2_result,
                self.bilby_job_completed_result
            ]
        })

        # Change the most recent job's creation time to be older and check that the order is correct
        self.bilby_job_incomplete.creation_time -= datetime.timedelta(hours=1)
        self.bilby_job_incomplete.save()

        self.bilby_job_incomplete_result['job']['creationTime'] = \
            graphene.DateTime().serialize(self.bilby_job_incomplete.creation_time)

        self.bilby_job_incomplete_result['job']['lastUpdated'] = \
            graphene.DateTime().serialize(self.bilby_job_incomplete.last_updated)

        fetch_jobs({
            'publicBilbyJobs': [
                self.bilby_job_completed2_result,
                self.bilby_job_completed_result,
                self.bilby_job_incomplete_result
            ]
        })
