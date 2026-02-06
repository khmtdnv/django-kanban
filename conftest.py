import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.boards.models import Board, Column
from apps.projects.models import Project


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    user = User.objects.create(phone_number="+79931384192")
    return user


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def project(user, db):
    project = Project.objects.create(name="Test Name", owner=user)
    project.members.set((user,))
    return project


@pytest.fixture
def board(project, db):
    board = Board.objects.create(name="Test Name", project=project)
    return board


@pytest.fixture
def column(board, db):
    column = Column.objects.create(name="Test Name", board=board)
    return column
