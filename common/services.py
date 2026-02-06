from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Max
from rest_framework.exceptions import ValidationError

from apps.boards.models import Board, Column
from apps.projects.models import Project
from apps.tasks.models import Task

User = get_user_model()


class BaseService:
    def __init__(self, project: Project):
        self.project = project

    def ensure_same_project(self, obj, obj_name: str):
        if obj and hasattr(obj, "project") and obj.project != self.project:
            raise ValidationError(
                {obj_name: f"Этот {obj_name} относится к другому проекту"}
            )


class TaskCreationService(BaseService):
    def __init__(self, project: Project, data: dict):
        super().__init__(project)
        self.data = data

    def _validate(self, parent: Task = None):  # type:ignore
        if parent:
            self.ensure_same_project(parent, "parent_task")
            if parent.parent:
                raise ValidationError(
                    {
                        "parent": "Нельзя создать подзадачу у задач, которые сами являются подзадачами"
                    }
                )

        column = self.data.get("column")
        if column:
            self.ensure_same_project(column.board, "column")

        sprint = self.data.get("sprint")
        if sprint:
            self.ensure_same_project(sprint, "sprint")

        assignee = self.data.get("assignee")
        if assignee:
            is_owner = assignee == self.project.owner
            is_member = self.project.members.filter(id=assignee.id).exists()
            if not is_owner and not is_member:
                raise ValidationError(
                    {"assignee": "Исполнитель не является участником проекта"}
                )

    def execute(self, parent: Task = None) -> Task:  # type:ignore
        self._validate(parent=parent)
        labels = self.data.pop("labels", [])

        with transaction.atomic():
            task = Task.objects.create(
                project=self.project,
                parent=parent,
                **self.data,
            )
            if labels:
                task.labels.set(labels)
        return task


class TaskUpdateService(BaseService):
    def __init__(self, project: Project, task: Task, data: dict):
        super().__init__(project)
        self.task = task
        self.data = data

    def _validate(self):
        self.ensure_same_project(self.task, "task")
        column = self.data.get("column")
        if column:
            self.ensure_same_project(column.board, "column")

        sprint = self.data.get("sprint")
        if sprint:
            self.ensure_same_project(sprint, "sprint")

        assignee = self.data.get("assignee")
        if assignee:
            is_owner = assignee == self.project.owner
            is_member = self.project.members.filter(id=assignee.id).exists()
            if not is_owner and not is_member:
                raise ValidationError(
                    {"assignee": "Исполнитель не является участником проекта"}
                )

    def execute(self) -> Task:
        self._validate()
        labels = self.data.pop("labels", None)

        with transaction.atomic():
            for key, value in self.data.items():
                setattr(self.task, key, value)
            self.task.save()

            if labels is not None:
                self.task.labels.set(labels)
        return self.task


class TaskDeletionService(BaseService):
    def __init__(self, project: Project, task: Task):
        super().__init__(project)
        self.task = task

    def _validate(self):
        self.ensure_same_project(self.task, "task")

    def execute(self):
        self._validate()
        self.task.delete()


class TaskMoveService(BaseService):
    def __init__(self, project: Project, task: Task, column: Column):
        super().__init__(project)
        self.task = task
        self.column = column

    def _validate(self):
        self.ensure_same_project(self.task, "task")
        self.ensure_same_project(self.column.board, "column")

    def execute(self) -> Task:
        self._validate()
        self.task.column = self.column
        self.task.save()
        return self.task


class AssignService(BaseService):
    def __init__(self, project: Project, task: Task, assignee: User):
        super().__init__(project)
        self.task = task
        self.assignee = assignee

    def _validate(self):
        self.ensure_same_project(self.task, "task")
        if self.assignee == self.task.assignee:
            raise ValidationError({"assignee": "Этот пользователь уже назначен"})

        is_owner = self.assignee == self.project.owner
        is_member = self.project.members.filter(
            id=self.assignee.id  # type:ignore
        ).exists()
        if not is_owner and not is_member:
            raise ValidationError(
                {"assignee": "Исполнитель не является участником проекта"}
            )

    def execute(self) -> Task:
        self._validate()
        self.task.assignee = self.assignee
        self.task.save()
        return self.task


class BoardCreationService(BaseService):
    def __init__(self, project: Project, data: dict):
        super().__init__(project)
        self.data = data

    def _validate(self):
        if Board.objects.filter(
            project=self.project, name=self.data.get("name")
        ).exists():
            raise ValidationError(
                {"name": "Доска с таким именем уже существует в проекте"}
            )

    def execute(self) -> Board:
        self._validate()
        return Board.objects.create(name=self.data["name"], project=self.project)


class BoardUpdateService(BaseService):
    def __init__(self, board: Board, data: dict, project: Project):
        super().__init__(project)
        self.board = board
        self.data = data

    def _validate(self):
        self.ensure_same_project(self.board, "board")
        if "name" in self.data:
            if (
                Board.objects.filter(project=self.project, name=self.data["name"])
                .exclude(id=self.board.id)  # type:ignore
                .exists()
            ):
                raise ValidationError({"name": "Доска с таким именем уже существует"})

    def execute(self) -> Board:
        self._validate()
        for key, value in self.data.items():
            setattr(self.board, key, value)
        self.board.save()
        return self.board


class BoardDeletionService(BaseService):
    def __init__(self, board: Board, project: Project):
        super().__init__(project)
        self.board = board

    def _validate(self):
        self.ensure_same_project(self.board, "board")

    def execute(self):
        self._validate()
        self.board.delete()


class ColumnCreationService(BaseService):
    def __init__(self, board: Board, data: dict, project: Project):
        super().__init__(project)
        self.board = board
        self.data = data

    def _validate(self):
        self.ensure_same_project(self.board, "board")
        name = self.data.get("name")
        if not name:
            raise ValidationError({"name": "Название колонки обязательно"})
        if Column.objects.filter(board=self.board, name=name).exists():
            raise ValidationError({"name": "Колонка с таким названием уже существует"})

    def execute(self) -> Column:
        self._validate()
        with transaction.atomic():
            agg = self.board.columns.aggregate(Max("order"))  # type:ignore
            max_order = agg["order__max"] if agg["order__max"] is not None else -1
            column = Column.objects.create(
                name=self.data["name"],
                board=self.board,
                order=max_order + 1,
            )
        return column


class ColumnUpdateService(BaseService):
    def __init__(self, column: Column, data: dict, project: Project):
        super().__init__(project)
        self.column = column
        self.data = data

    def _validate(self):
        self.ensure_same_project(self.column.board, "column")

    def execute(self) -> Column:
        self._validate()
        for key, value in self.data.items():
            setattr(self.column, key, value)
        self.column.save()
        return self.column


class ColumnReorderService(BaseService):
    def __init__(self, board: Board, ordered_column_ids: list[int], project: Project):
        super().__init__(project)
        self.board = board
        self.ordered_column_ids = ordered_column_ids

    def _validate(self):
        self.ensure_same_project(self.board, "board")
        existing_ids = set(
            self.board.columns.values_list("id", flat=True)  # type:ignore
        )
        incoming_ids = set(self.ordered_column_ids)

        if len(existing_ids) != len(self.ordered_column_ids):
            raise ValidationError({"detail": f"Ожидается {len(existing_ids)} колонок"})

        if existing_ids != incoming_ids:
            raise ValidationError({"detail": "Передан некорректный список ID"})

    def execute(self) -> list[Column]:
        self._validate()
        with transaction.atomic():
            self.board.columns.update(order=F("order") + 10000)  # type:ignore

            updates = [
                Column(id=column_id, order=new_order)
                for new_order, column_id in enumerate(self.ordered_column_ids)
            ]
            Column.objects.bulk_update(updates, fields=["order"], batch_size=100)

        return list(self.board.columns.order_by("order"))  # type:ignore


class ProjectCreationService:
    def __init__(self, user, data: dict):
        self.user = user
        self.data = data

    def _validate(self):
        if Project.objects.filter(name=self.data.get("name")).exists():
            raise ValidationError({"name": "Проект с таким именем уже существует"})

    def execute(self) -> Project:
        self._validate()
        with transaction.atomic():
            project = Project.objects.create(
                name=self.data.get("name"),
                owner=self.user,
            )
            project.members.add(self.user)
        return project


class ProjectUpdateService:
    def __init__(self, project: Project, data: dict):
        self.project = project
        self.data = data

    def execute(self) -> Project:
        for key, value in self.data.items():
            setattr(self.project, key, value)
        self.project.save()
        return self.project


class ProjectDeletionService:
    def __init__(self, project: Project):
        self.project = project

    def execute(self):
        self.project.delete()


class ProjectAddMembersService:
    def __init__(self, project: Project, member_ids: list[int]):
        self.project = project
        self.member_ids = member_ids

    def _validate(self):
        existing_users = User.objects.filter(pk__in=self.member_ids)
        if existing_users.count() != len(self.member_ids):
            raise ValidationError({"detail": "Часть пользователей не найдена"})

        return existing_users.exclude(
            pk__in=self.project.members.values_list("pk", flat=True)
        )

    def execute(self) -> Project:
        new_members = self._validate()
        if new_members.exists():
            self.project.members.add(*new_members)
        return self.project


class ProjectRemoveMemberService:
    def __init__(self, project: Project, data: dict):
        self.project = project
        self.data = data

    def execute(self):
        self.project.members.remove(self.data["member_id"])
