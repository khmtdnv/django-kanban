from django.urls import reverse
from rest_framework import status


def test_board_create(auth_client, project, db):
    url = reverse("board-list")
    data = {"name": "Test Name", "project": project.pk}
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED


def test_board_list(auth_client, project, db):
    url = reverse("board-list")
    query_params = {"project": project.pk}
    response = auth_client.get(url, query_params)
    assert response.status_code == status.HTTP_200_OK


def test_board_retrieve(auth_client, board, db):
    url = reverse("board-detail", kwargs={"pk": board.pk})
    query_params = {"project": board.project.pk}
    response = auth_client.get(url, query_params)
    assert response.status_code == status.HTTP_200_OK


def test_board_update_column(auth_client, column, db):
    url = reverse(
        "board-update-column",
        kwargs={"pk": column.board.pk, "column_id": column.pk},
    )
    data = {"name": "Another Name", "project": column.board.project.pk}
    response = auth_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
