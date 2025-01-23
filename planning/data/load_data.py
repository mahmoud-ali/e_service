import csv

from django.contrib.auth import get_user_model

from ..models import Department, Goal, Task, TaskDuration

admin_user = get_user_model().objects.get(id=1)

def import_tasks(year=2025,file_name='planning.csv'):
    with open('./planning/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                main_goal_txt = row[0].strip()
                sub_goal_txt = row[1].strip()
                resp_txt = row[2].strip()
                task_txt = row[3].strip()

                department, _ = Department.objects.get_or_create(
                    # user=admin_user,
                    name=resp_txt,
                )

                main_goal, _ = Goal.objects.get_or_create(
                    code='1',
                    name=main_goal_txt,
                )

                sub_goal, _ = Goal.objects.get_or_create(
                    parent=main_goal,
                    code='12',
                    name=sub_goal_txt,
                )

                task, _ = Task.objects.get_or_create(
                    goal=sub_goal,
                    year=year,
                    name=task_txt,
                    responsible=department,
                )

                for m in range(1,13):
                    TaskDuration.objects.get_or_create(
                        task=task,
                        month=m,
                    )

            except Exception as e:
                print(f"task: {main_goal_txt}/{task_txt}, Exception: {e}")


def import_quantity_tasks(year=2025,file_name='quantity.csv'):
    with open('./planning/data/'+file_name, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers

        main_goal = Goal.objects.get(
            code='7',
        )

        for row in reader:
            try:
                main_goal_txt = row[0].strip()
                sub_goal_txt = row[1].strip()
                sub_goal_code_txt = row[4].strip()
                resp_txt = row[2].strip()
                task_txt = row[3].strip()

                department, _ = Department.objects.get_or_create(
                    # user=admin_user,
                    name=resp_txt,
                )

                sub_goal, _ = Goal.objects.get_or_create(
                    parent=main_goal,
                    code=sub_goal_code_txt,
                    name=sub_goal_txt,
                )

                task, _ = Task.objects.get_or_create(
                    goal=sub_goal,
                    year=year,
                    name=task_txt,
                    responsible=department,
                )

                for m in range(1,13):
                    TaskDuration.objects.get_or_create(
                        task=task,
                        month=m,
                    )

            except Exception as e:
                print(f"task: {main_goal_txt}/{task_txt}, Exception: {e}")

