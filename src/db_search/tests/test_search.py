import datetime

from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from gwauth.models import GWCloudUser
from jobserver.models import Job, JobHistory
from bilbyui.models import BilbyJob, Label
from viterbi.models import ViterbiJob

from db_search.status import JobStatus
from db_search.utils.job_search import job_search


@override_settings(TESTING=True)
class TestSearch(SimpleTestCase):
    databases = '__all__'

    def setUp(self):
        self.maxDiff = 999999

        # Clean everything up first just in case - because we are unable to use TransactionTestCase which would normally
        # manage this for us
        GWCloudUser.objects.using('gwauth').all().delete()
        Job.objects.using('jobserver').all().delete()
        JobHistory.objects.using('jobserver').all().delete()
        BilbyJob.objects.using('bilbyui').all().delete()
        Label.objects.using('bilbyui').all().delete()

        # Insert users
        self.user_1 = GWCloudUser.objects.using('gwauth').create(
            email='user1@example.com',
            username='user1',
            first_name='User',
            last_name='One magenta'
        )

        self.user_2 = GWCloudUser.objects.using('gwauth').create(
            email='user2@example.com',
            username='user2',
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

        # Uploaded bilby job
        self.uploaded_bilby_job1 = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_completed.user,
            job_controller_id=None,
            name="test_job_uploaded",
            description="my potato job is magenta",
            private=False,
            is_uploaded_job=True
        )

        self.uploaded_bilby_job2 = BilbyJob.objects.using('bilbyui').create(
            user_id=self.job_controller_job_completed.user,
            job_controller_id=None,
            name="test_job_uploaded2",
            description="my grape job is fermented",
            private=False,
            is_uploaded_job=True,
            is_ligo_job=True
        )

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

        self.label_bad_run = Label.objects.using('bilbyui').create(
            name='Bad Run',
            description='This run contains some issues and should not be used for science.',
        )

        self.label_production_run = Label.objects.using('bilbyui').create(
            name='Production Run',
            description='This run has been completed successfully and can be used for science.',
        )

        self.label_review_requested = Label.objects.using('bilbyui').create(
            name='Review Requested',
            description='This run should be reviewed by peers.',
        )

        self.label_reviewed = Label.objects.using('bilbyui').create(
            name='Reviewed',
            description='This run has been reviewed.',
        )

        self.bilby_job_completed.labels.add(self.label_bad_run)
        self.bilby_job_completed.labels.add(self.label_review_requested)

        self.bilby_job_incomplete.labels.add(self.label_bad_run)

        self.bilby_job_error.labels.add(self.label_bad_run)

        self.bilby_job_completed2.labels.add(self.label_production_run)
        self.bilby_job_completed2.labels.add(self.label_reviewed)

    def test_no_terms(self):
        expected = [
            {
                'user': self.user_1,
                'history': [
                    self.job_controller_job_completed_history1
                ],
                'job': self.bilby_job_completed
            },
            {
                'user': self.user_2,
                'history': [
                    self.job_controller_job_completed2_history3,
                    self.job_controller_job_completed2_history2,
                    self.job_controller_job_completed2_history1
                ],
                'job': self.bilby_job_completed2
            },
            {
                'user': self.user_1,
                'history': [],
                'job': self.uploaded_bilby_job1
            },
            {
                'user': self.user_1,
                'history': [],
                'job': self.uploaded_bilby_job2
            },
            {
                'user': self.user_2,
                'history': [
                    self.job_controller_job_incomplete_history1
                ],
                'job': self.bilby_job_incomplete
            }
        ]

        end_time = timezone.now() - datetime.timedelta(days=1)

        # Test that all results are returned as expected
        results = job_search('bilbyui', [], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, expected)

        # Test range limiting
        results = job_search('bilbyui', [], end_time, None, 0, 1, False)
        self.assertSequenceEqual(results, expected[:1])

        results = job_search('bilbyui', [], end_time, None, 0, 2, False)
        self.assertSequenceEqual(results, expected[:2])

        # Test slicing
        results = job_search('bilbyui', [], end_time, None, 1, 1, False)
        self.assertSequenceEqual(results, expected[1:2])

        results = job_search('bilbyui', [], end_time, None, 1, 2, False)
        self.assertSequenceEqual(results, expected[1:3])

        results = job_search('bilbyui', [], end_time, None, 2, 1, False)
        self.assertSequenceEqual(results, expected[2:3])

        # Test out of bounds returns an empty array (No results)
        results = job_search('bilbyui', [], end_time, None, 2000, 20, False)
        self.assertSequenceEqual(results, [])

        # Test that the time filter works as expected
        self.job_controller_job_completed_history1.timestamp = end_time
        self.job_controller_job_completed_history1.save()

        results = job_search('bilbyui', [], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, expected)

        self.job_controller_job_completed_history1.timestamp = end_time - datetime.timedelta(seconds=1)
        self.job_controller_job_completed_history1.save()

        results = job_search('bilbyui', [], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, expected[1:])

        self.job_controller_job_completed_history1.timestamp = timezone.now()
        self.job_controller_job_completed_history1.save()

        results = job_search('bilbyui', [], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, expected)

        # Check private jobs are excluded
        self.bilby_job_completed.private = True
        self.bilby_job_completed.save()

        results = job_search('bilbyui', [], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, expected[1:])

        self.bilby_job_completed.private = False
        self.bilby_job_completed.save()

        results = job_search('bilbyui', [], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, expected)

        # Check that a job that completes is still reported correctly
        self.job_controller_job_incomplete_history2 = JobHistory.objects.using('jobserver').create(
            job=self.job_controller_job_incomplete,
            what='_job_completion_',
            state=JobStatus.COMPLETED,
            timestamp=timezone.now()
        )

        expected[-1]['history'] = [
            self.job_controller_job_incomplete_history2,
            self.job_controller_job_incomplete_history1
        ]
        results = job_search('bilbyui', [], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, expected)

        self.job_controller_job_incomplete_history2.delete()

    def test_single_term(self):
        job_completed = {
            'user': self.user_1,
            'history': [
                self.job_controller_job_completed_history1
            ],
            'job': self.bilby_job_completed
        }
        job_completed2 = {
            'user': self.user_2,
            'history': [
                self.job_controller_job_completed2_history3,
                self.job_controller_job_completed2_history2,
                self.job_controller_job_completed2_history1
            ],
            'job': self.bilby_job_completed2
        }
        job_incomplete = {
            'user': self.user_2,
            'history': [
                self.job_controller_job_incomplete_history1
            ],
            'job': self.bilby_job_incomplete
        }
        job_uploaded1 = {
            'user': self.user_1,
            'history': [],
            'job': self.uploaded_bilby_job1
        }
        job_uploaded2 = {
            'user': self.user_1,
            'history': [],
            'job': self.uploaded_bilby_job2
        }

        end_time = timezone.now() - datetime.timedelta(days=1)

        # Test user names

        # Should match all jobs since username starts with user for both test users
        results = job_search('bilbyui', ['user'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_completed2,
                job_uploaded1,
                job_uploaded2,
                job_incomplete
            ]
        )

        # Should match jobs by just user 1
        results = job_search('bilbyui', ['magenta'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_uploaded1,
                job_uploaded2
            ]
        )

        # Should match jobs by just user 2
        results = job_search('bilbyui', ['yellow'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2,
                job_incomplete
            ]
        )

        # Test user first name
        # Should match jobs by just user 2
        results = job_search('bilbyui', ['another'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2,
                job_incomplete
            ]
        )

        # Test user last name
        # Should match jobs by just user 1
        results = job_search('bilbyui', ['one'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_uploaded1,
                job_uploaded2
            ]
        )

        # Should match jobs by just user 2
        results = job_search('bilbyui', ['two'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2,
                job_incomplete
            ]
        )

        # Test job name
        # Should match all jobs
        results = job_search('bilbyui', ['test_job'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_completed2,
                job_uploaded1,
                job_uploaded2,
                job_incomplete
            ]
        )

        # Should match only completed2
        results = job_search('bilbyui', ['test_job_purple'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        # Test job description
        results = job_search('bilbyui', ['potato'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_uploaded1,
                job_incomplete
            ]
        )

        results = job_search('bilbyui', ['brown'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed
            ]
        )

        results = job_search('bilbyui', ['cyan'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search('bilbyui', ['violet'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_incomplete
            ]
        )

        # Double check case insensitivity
        # Should match all jobs
        results = job_search('bilbyui', ['tEsT_jOb'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_completed2,
                job_uploaded1,
                job_uploaded2,
                job_incomplete
            ]
        )

        # Should match only completed2
        results = job_search('bilbyui', ['TeSt_JoB_pUrPlE'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        # Test job description
        results = job_search('bilbyui', ['POTATO'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_uploaded1,
                job_incomplete
            ]
        )

        # Test labels
        results = job_search('bilbyui', ['production'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search('bilbyui', ['REVIEWED'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search('bilbyui', ['bad'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_incomplete
            ]
        )

        results = job_search('bilbyui', ['review'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_completed2
            ]
        )

        # Test non existent terms
        results = job_search('bilbyui', ['blue'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            []
        )

        results = job_search('bilbyui', ['orange'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            []
        )

    def test_multiple_terms(self):
        job_completed = {
            'user': self.user_1,
            'history': [
                self.job_controller_job_completed_history1
            ],
            'job': self.bilby_job_completed
        }
        job_completed2 = {
            'user': self.user_2,
            'history': [
                self.job_controller_job_completed2_history3,
                self.job_controller_job_completed2_history2,
                self.job_controller_job_completed2_history1
            ],
            'job': self.bilby_job_completed2
        }
        job_incomplete = {
            'user': self.user_2,
            'history': [
                self.job_controller_job_incomplete_history1
            ],
            'job': self.bilby_job_incomplete
        }
        job_uploaded1 = {
            'user': self.user_1,
            'history': [],
            'job': self.uploaded_bilby_job1
        }
        job_uploaded2 = {
            'user': self.user_1,
            'history': [],
            'job': self.uploaded_bilby_job2
        }

        end_time = timezone.now() - datetime.timedelta(days=1)

        # Should match all jobs
        results = job_search('bilbyui', ['test', 'job'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_completed2,
                job_uploaded1,
                job_uploaded2,
                job_incomplete
            ]
        )

        # Should match all jobs
        results = job_search(
            'bilbyui',
            ['test', 'job', 'test', 'job', 'test', 'job', 'test', 'job'],
            end_time, None, 0, 20, False
        )
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_completed2,
                job_uploaded1,
                job_uploaded2,
                job_incomplete
            ]
        )

        # Should only match completed2
        results = job_search('bilbyui', ['test', 'job', 'purple'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search(
            'bilbyui',
            ['test', 'job', 'purple', 'actually', 'cyan', 'yellow', 'another', 'two'],
            end_time, None, 0, 20, False
        )
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        # Should match nothing
        results = job_search(
            'bilbyui',
            ['test', 'job', 'purple', 'actually', 'cyan', 'yellow', 'another', 'two', 'blue'],
            end_time, None, 0, 20, False
        )
        self.assertSequenceEqual(results, [])

        # Should match only the incomplete job
        results = job_search('bilbyui', ['potato', 'two'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_incomplete
            ]
        )

        # Check matching tags
        results = job_search('bilbyui', ['review', 'ReQuEsTeD'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed
            ]
        )

        results = job_search('bilbyui', ['bad', 'run'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed,
                job_incomplete
            ]
        )

        results = job_search('bilbyui', ['purple', 'production'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search('bilbyui', ['purple', 'production', 'review'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search('bilbyui', ['purple', 'production', 'reviewed'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search('bilbyui', ['purple', 'production', 'review', 'test'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed2
            ]
        )

        results = job_search(
            'bilbyui', ['purple', 'production', 'reviewed', 'test', 'brown'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, [])

        results = job_search('bilbyui',
                             ['purple', 'production', 'reviewed', 'test', 'bad'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(results, [])

    def test_single_term_viterbi(self):
        job_completed = {
            'user': self.user_1,
            'history': [
                self.job_controller_job_completed_history1_viterbi
            ],
            'job': self.job_completed_viterbi
        }

        end_time = timezone.now() - datetime.timedelta(days=1)

        # Test user names

        # Should match all jobs since username starts with user for both test users
        results = job_search('viterbi', ['user'], end_time, None, 0, 20, False)
        self.assertSequenceEqual(
            results,
            [
                job_completed
            ]
        )

    def test_exclude_ligo_jobs(self):
        expected = [
            {
                'user': self.user_2,
                'history': [
                    self.job_controller_job_completed2_history3,
                    self.job_controller_job_completed2_history2,
                    self.job_controller_job_completed2_history1
                ],
                'job': self.bilby_job_completed2
            },
            {
                'user': self.user_1,
                'history': [],
                'job': self.uploaded_bilby_job1
            },
            {
                'user': self.user_2,
                'history': [
                    self.job_controller_job_incomplete_history1
                ],
                'job': self.bilby_job_incomplete
            }
        ]

        end_time = timezone.now() - datetime.timedelta(days=1)

        # Test that all results are returned as expected
        results = job_search('bilbyui', [], end_time, None, 0, 20, True)
        self.assertSequenceEqual(results, expected)

        for result in results:
            self.assertFalse(result['job'].is_ligo_job)
