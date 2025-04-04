from celery import shared_task


@shared_task(
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=300,
    # autoretry_for=(WhateverError,),
)
def send_alert(*args, **kwargs):
    pass
