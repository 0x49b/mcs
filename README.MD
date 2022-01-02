Worker
```
celery -A mcs worker -l INFO
```

Beat
```
celery -A mcs beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Worker with beat
```
celery -A mcs worker -l INFO -B
```
dont forget redis 

https://medium.com/clean-slate-technologies/deploy-celery-and-celery-beat-in-production-with-django-ubuntu-de71ccb24907