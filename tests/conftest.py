import pytest


@pytest.fixture(autouse=True)
def _stop_job_worker():
    """The job worker is a background thread; stop it after each test so it never reads another test's data."""
    yield
    from studio import jobs
    jobs.stop_worker()
