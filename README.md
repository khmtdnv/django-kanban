Запуск celery:
```shell
celery --app config.celery worker -l info
```
Запуск Flower(celery):
```shell
celery --app config.celery flower
```


Feature branches:
```shell
git checkout develop
git checkout -b feature_branch

git add .
git commit
git push

git checkout develop
git merge feature_branch
```

Pre-commit:
```shell
pre-commit uninstall
pre-commit install
pre-commit run --all-files
```

docker build --network=host -f Dockerfile --target staging -t task-manager:staging .
