from bilby.status import JobStatus


def derive_job_status(history):
    """
    Takes a job history returned from the job controller and turns it in to a final status

    :param history: The job history object returned from the job controller
    """
    if len(history):
        return JobStatus.display_name(history[0].state)

    return "Unknown"
