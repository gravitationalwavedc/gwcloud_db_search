sql_term_search = """
SELECT
    id
FROM
    {job_table}
WHERE
    (
        user_id IN (
            SELECT
                id
            FROM
                {auth_database}.gwauth_gwclouduser
            WHERE
                first_name LIKE %(term)s
                OR last_name LIKE %(term)s
        )
        OR {job_table}.name LIKE %(term)s
        OR {job_table}.description LIKE %(term)s
        OR id IN (
            SELECT
                {job_label_table}.{job_model_name}job_id
            FROM
                {job_label_table}
            WHERE
                {job_label_table}.label_id IN (
                    SELECT
                        {label_table}.id
                    FROM
                        {label_table}
                    WHERE
                        name LIKE %(term)s
                )
        )
        OR event_id_id IN (
            SELECT
                {event_id_table}.id
            FROM
                {event_id_table}
            WHERE
                event_id LIKE %(term)s
                OR trigger_id LIKE %(term)s
                OR nickname LIKE %(term)s
        )
    )
    AND
    (
        (
            job_controller_id in (
                SELECT
                    {jobcontroller_database}.jobserver_job.id
                FROM
                    {jobcontroller_database}.jobserver_job
                INNER JOIN
                    {jobcontroller_database}.jobserver_jobhistory ON
                        (
                            {jobcontroller_database}.jobserver_job.id =
                            {jobcontroller_database}.jobserver_jobhistory.job_id
                        )
                WHERE
                    {jobcontroller_database}.jobserver_jobhistory.timestamp >= %(end_time)s
                    AND (
                        SELECT
                            {jobcontroller_database}.jobserver_jobhistory.state
                        FROM
                            {jobcontroller_database}.jobserver_jobhistory
                        WHERE
                            {jobcontroller_database}.jobserver_jobhistory.job_id =
                            {jobcontroller_database}.jobserver_job.id
                        ORDER BY {jobcontroller_database}.jobserver_jobhistory.timestamp DESC
                        LIMIT 1
                    ) in %(valid_states)s
                    AND application = %(application)s
            )
            AND {job_table}.job_type = 0
        )
        OR (
            {job_table}.job_type IN (1, 2)
            AND {job_table}.creation_time >= %(end_time)s
        )
    )
    AND {job_table}.private = FALSE
    AND {job_table}.is_ligo_job IN %(ligo_job_states)s
"""
