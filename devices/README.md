
# Evreka Case

### How to run

```bash
docker compose -f docker/docker-compose.yaml -p evreka up --build
```

### How to run tests

```bash
docker compose -f docker/docker-compose.yaml -p evreka up -d
docker exec -it evreka-backend bash
python manage.py test
```
