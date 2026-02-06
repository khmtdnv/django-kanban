# import random
# from datetime import timedelta

# from django.contrib.auth import get_user_model
# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from faker import Faker

# from apps.projects.models import Project

# # Импорт моделей колонок, если они нужны для ForeignKey, или используй ID

# User = get_user_model()
# fake = Faker(["ru_RU"])


# class Command(BaseCommand):
#     help = "БЫСТРОЕ создание 1M+ записей через bulk_create"

#     def handle(self, *args, **kwargs):
#         BATCH_SIZE = 5000  # Размер пачки для вставки
#         TOTAL_TASKS = 1_000_000  # Сколько задач хотим

#         # 1. Быстро создаем 1000 пользователей
#         self.stdout.write("Генерация пользователей...")
#         users_batch = []
#         for i in range(1000):
#             # Генерируем уникальные телефоны математически, чтобы не было коллизий
#             # +79000000000, +79000000001...
#             phone = f"+7900{i:07d}"
#             users_batch.append(User(phone_number=phone, is_active=True))

#         # ignore_conflicts=True пропустит дубликаты, если запустишь скрипт дважды
#         User.objects.bulk_create(users_batch, ignore_conflicts=True)

#         # Получаем список ID всех пользователей, чтобы привязывать к ним задачи
#         # values_list возвращает кортежи, flat=True возвращает список ID
#         user_ids = list(User.objects.values_list("id", flat=True))

#         if not user_ids:
#             self.stdout.write(self.style.ERROR("Не удалось создать пользователей"))
#             return

#         # 2. Создаем 100 проектов (распределяем их по случайным юзерам)
#         self.stdout.write("Генерация проектов...")
#         projects_batch = []
#         for i in range(100):
#             projects_batch.append(
#                 Project(
#                     name=f"Project {i}",
#                     owner_id=random.choice(user_ids),
#                     description="Auto-generated high load project",
#                 )
#             )
#         Project.objects.bulk_create(projects_batch, ignore_conflicts=True)
#         project_ids = list(Project.objects.values_list("id", flat=True))

#         # 3. Самое главное: Генерируем 1 000 000 задач
#         self.stdout.write(
#             f"Начинаем генерацию {TOTAL_TASKS} задач. Это займет время..."
#         )

#         tasks_batch = []
#         # statuses = ["TODO", "IN_PROGRESS", "TESTING", "DONE"]  # Твои статусы
#         priorities = Task.Priority.values
#         now = timezone.now()

#         count = 0
#         for i in range(TOTAL_TASKS):
#             # Подготовка данных в памяти (это очень быстро)
#             created_at = now - timedelta(days=random.randint(0, 365))

#             task = Task(
#                 name=f"Load Test Task {i}",
#                 description="Fix the critical bug in production",
#                 priority=random.choice(priorities),
#                 project_id=random.choice(project_ids),
#                 assignee_id=random.choice(user_ids),
#                 created_at=created_at,  # Поле для сортировки
#             )
#             tasks_batch.append(task)

#             # Как только набрали пачку - сохраняем
#             if len(tasks_batch) >= BATCH_SIZE:
#                 Task.objects.bulk_create(tasks_batch)
#                 tasks_batch = []  # Очищаем список
#                 count += BATCH_SIZE
#                 self.stdout.write(f"   ...сохранено {count} задач")

#         # Сохраняем остатки, если не кратно BATCH_SIZE
#         if tasks_batch:
#             Task.objects.bulk_create(tasks_batch)

#         self.stdout.write(
#             self.style.SUCCESS(f"Готово! В базе теперь > {TOTAL_TASKS} задач.")
#         )
