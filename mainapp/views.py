from django.http import HttpResponsePermanentRedirect, Http404
from django.shortcuts import render
from .models import *
from .forms import *
import hashlib
import uuid
import datetime
import calendar

SALT = "e30c7b39f0d2478ea0e3e3d255c969f7"
MONTHS = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]

def getHashPassword(password, salt):
    return hashlib.sha3_224(bytes(password + SALT + salt, encoding="utf-8")).hexdigest()

def getUserFromSession(request):
    user = None
    try:
        user = User.objects.get(id=request.session.get("user_id"))
    except User.DoesNotExist:
        pass
    return user

def wideView(request, name_file):
    context = {
        "sections": Section.objects.all(),
        "user": getUserFromSession(request),
    }
    return render(request, name_file, context=context)

def adminRights(request):
    user = getUserFromSession(request)
    if user is None or user.role == 3 or user.role == 2:
        raise Http404

# ----------------------Обработка ошибок----------------------------------------------------- #

def e_handler404(request, exception):
    return render(request, "error/error.html", context={"title": "404 – страница не найдена"})

# ----------------------Авторизация и регистрация--------------------------------------------- #

def authorization(request):
    if request.method == "POST":
        try:
            account = Account.objects.get(login=request.POST.get("login"))
            if len(request.POST.get("password")) >= 12 and account.password == getHashPassword(request.POST.get("password"), account.salt):
                request.session["user_id"] = account.user.id
                return HttpResponsePermanentRedirect("/")
        except Account.DoesNotExist:
            pass
        return render(request, "authorization-registration/authorization.html", context={"error": "Неверный логин или пароль"})
    else:
        if getUserFromSession(request) is not None:
            raise Http404
        return render(request, "authorization-registration/authorization.html")

def register(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, request.FILES)
        if user_form.is_valid():
            del user_form.cleaned_data["repeat_password"]
            user_form.cleaned_data["role"] = 3
            login = user_form.cleaned_data.pop("login")
            password = user_form.cleaned_data.pop("password")
            if Account.objects.filter(login=login).count() > 0:
                return render(request, "authorization-registration/register.html", context={"error": "Такой логин уже существует"})
            user = User.objects.create(**user_form.cleaned_data)
            salt = uuid.uuid4().hex
            Account.objects.create(login=login,
                                   salt=salt,
                                   password=getHashPassword(password, salt),
                                   user=user)
            return HttpResponsePermanentRedirect("authorization")
        else:
            return render(request, "authorization-registration/register.html", context={"error": "Неправильный ввод данных"})
    else:
        if getUserFromSession(request) is not None:
            raise Http404
        return render(request, "authorization-registration/register.html")

# ----------------------Главная------------------------------------------------------------ #

def index(request):
    if "message" in request.session:
        message = request.session["message"]
        del request.session["message"]
        return render(request, "main/index.html", context={"message": message, "sections": Section.objects.all(), "user": getUserFromSession(request)})
    return wideView(request, "main/index.html")

def termsOfService(request):
    return wideView(request, "main/terms-of-service.html")

def contact(request):
    return wideView(request, "main/contact-us.html")

def information(request):
    return wideView(request, "main/site-information.html")

# ----------------------Профиль пользователя----------------------------------------------- #

def profile(request):
    context = {
        "sections": Section.objects.all(),
        "user": getUserFromSession(request),
    }
    if request.method == "POST":
        user = None
        try:
            user = User.objects.get(id=request.POST.get("user_id"))
        except (User.DoesNotExist, ValueError):
            pass
        password = request.POST.get("password")
        new_password = request.POST.get("new-password")
        if password != new_password and len(password) >= 12 and len(new_password) >= 12 and user is not None and user.id == getUserFromSession(request).id:
            if user.account.password == getHashPassword(password, user.account.salt):
                user.account.salt = uuid.uuid4().hex
                user.account.password = getHashPassword(new_password, user.account.salt)
                user.account.save()
                request.session["message"] = "Пароль успешно изменен"
                return HttpResponsePermanentRedirect("/")
        context["outUser"] = getUserFromSession(request)
        context["error"] = "Неправильный ввод данных"
        return render(request, "profile/profile.html", context=context)
    else:
        if request.GET.get("Id") is not None:
            try:
                context["outUser"] = User.objects.get(id=request.GET.get("Id"))
            except User.DoesNotExist:
                raise Http404
        else:
            if getUserFromSession(request) is None:
                raise Http404
            context["outUser"] = getUserFromSession(request)
        return render(request, "profile/profile.html", context=context)

def edit(request):
    if request.method == "POST":
        edit_user_form = EditUserForm(request.POST)
        if edit_user_form.is_valid() and edit_user_form.cleaned_data["user_id"] == getUserFromSession(request).id:
            try:
                user = User.objects.get(id=edit_user_form.cleaned_data["user_id"])
            except User.DoesNotExist:
                return render(request, "error/error-data.html", context={"title": "Неправильный ввод данных"})
            user.surname = edit_user_form.cleaned_data["surname"]
            user.name = edit_user_form.cleaned_data["name"]
            user.middle_name = edit_user_form.cleaned_data["middle_name"]
            user.email = edit_user_form.cleaned_data["email"]
            user.phone_number = edit_user_form.cleaned_data["phone_number"]
            if "image" in request.FILES:
                user.image = request.FILES.get("image")
            login = edit_user_form.cleaned_data["login"]
            if Account.objects.filter(login=login).exclude(user=user).count() > 0:
                return render(request, "error/error-data.html", context={"title": "Такой логин уже существует"})
            user.account.login = login
            user.account.save()
            user.save()
            request.session["message"] = "Данные успешно изменены"
            return HttpResponsePermanentRedirect("/")
        else:
            return render(request, "error/error-data.html", context={"title": "Неправильный ввод данных"})
    else:
        raise Http404

def Exit(request):
    request.session.flush()
    return HttpResponsePermanentRedirect("/")

# ----------------------Секция------------------------------------------------------------- #

def section(request):
    Id = request.GET.get("Id")
    try:
        item = Section.objects.get(id=Id)
    except (Section.DoesNotExist, ValueError):
        raise Http404
    context = {
        "title_description": str(item.description)[:163] + "...",
        "title_progress": str(item.progress)[:163] + "...",
        "title_beginner": str(item.beginner)[:163] + "...",
        "sections": Section.objects.all(),
        "section": item,
        "coaches": User.objects.filter(sections__id=Id, role=2),
        "students": User.objects.filter(sections__id=Id, role=3),
        "user": getUserFromSession(request),
    }
    if request.GET.get("button") == "prev" and request.GET.get("month") and request.GET.get("year") and request.GET.get("month").isdigit() and request.GET.get("year").isdigit():
        month = int(request.GET.get("month")) - 1
        year = int(request.GET.get("year"))
        if month == 0:
            month = 12
            year = year - 1
    elif request.GET.get("button") == "next" and request.GET.get("month") and request.GET.get("year") and request.GET.get("month").isdigit() and request.GET.get("year").isdigit():
        month = int(request.GET.get("month")) + 1
        year = int(request.GET.get("year"))
        if month == 13:
            month = 1
            year = year + 1
    else:
        month = datetime.date.today().month
        year = datetime.date.today().year
    if month == datetime.date.today().month:
        context["day"] = datetime.date.today().day
    try:
        date = datetime.date(year=year, month=month, day=1)
    except ValueError:
        raise Http404
    context["calendar"] = calendar.monthcalendar(date.year, date.month)
    context["date"] = date
    context["month"] = MONTHS[date.month - 1]
    return render(request, "section/section.html", context=context)

def addStudents(request):
    if request.method == "POST":
        section_id = request.POST.get("section_id")
        if request.POST.get("button") == "button":
            item = Section.objects.get(id=section_id)
            for element in request.POST.getlist("arrayUserId"):
                user = User.objects.get(id=int(element))
                user.sections.add(item)
            return HttpResponsePermanentRedirect("section?Id=" + str(item.id))
        elif request.POST.get("button") == "sort":
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "section_id": section_id,
                "name_table": "Список свободных студентов",
                "title": "Список свободных студентов",
                "name_button": "Добавить"
            }
            if request.POST.get("criterion") == "surname":
                context["users"] = User.objects.filter(role=3).exclude(sections__id=section_id).order_by("surname")
            elif request.POST.get("criterion") == "name":
                context["users"] = User.objects.filter(role=3).exclude(sections__id=section_id).order_by("name")
            else:
                context["users"] = User.objects.filter(role=3).exclude(sections__id=section_id)
            return render(request, "section/list.html", context=context)
        else:
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "users": User.objects.filter(role=3).exclude(sections__id=section_id),
                "section_id": section_id,
                "name_table": "Список свободных студентов",
                "title": "Список свободных студентов",
                "name_button": "Добавить"
            }
            return render(request, "section/list.html", context=context)
    else:
        raise Http404

def addCoaches(request):
    if request.method == "POST":
        section_id = request.POST.get("section_id")
        if request.POST.get("button") == "button":
            item = Section.objects.get(id=section_id)
            for element in request.POST.getlist("arrayUserId"):
                user = User.objects.get(id=int(element))
                user.sections.add(item)
            return HttpResponsePermanentRedirect("section?Id=" + str(item.id))
        elif request.POST.get("button") == "sort":
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "section_id": section_id,
                "title": "Список свободных тренеров",
                "name_table": "Список свободных тренеров",
                "name_button": "Добавить"
            }
            if request.POST.get("criterion") == "surname":
                context["users"] = User.objects.filter(role=2).exclude(sections__id=section_id).order_by("surname")
            elif request.POST.get("criterion") == "name":
                context["users"] = User.objects.filter(role=2).exclude(sections__id=section_id).order_by("name")
            else:
                context["users"] = User.objects.filter(role=2).exclude(sections__id=section_id)
            return render(request, "section/list.html", context=context)
        else:
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "users": User.objects.filter(role=2).exclude(sections__id=section_id),
                "section_id": section_id,
                "title": "Список свободных тренеров",
                "name_table": "Список свободных тренеров",
                "name_button": "Добавить"
            }
            return render(request, "section/list.html", context=context)
    else:
        raise Http404

def deleteStudents(request):
    if request.method == "POST":
        section_id = request.POST.get("section_id")
        if request.POST.get("button") == "button":
            item = Section.objects.get(id=section_id)
            for element in request.POST.getlist("arrayUserId"):
                user = User.objects.get(id=int(element))
                item.user_set.remove(user)
            return HttpResponsePermanentRedirect("section?Id=" + str(item.id))
        elif request.POST.get("button") == "sort":
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "section_id": section_id,
                "name_table": "Список занимающихся студентов",
                "title": "Список занимающихся студентов",
                "name_button": "Исключить"
            }
            if request.POST.get("criterion") == "surname":
                context["users"] = User.objects.filter(sections__id=section_id, role=3).order_by("surname")
            elif request.POST.get("criterion") == "name":
                context["users"] = User.objects.filter(sections__id=section_id, role=3).order_by("name")
            else:
                context["users"] = User.objects.filter(sections__id=section_id, role=3)
            return render(request, "section/list.html", context=context)
        else:
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "users": User.objects.filter(sections__id=section_id, role=3),
                "section_id": section_id,
                "name_table": "Список занимающихся студентов",
                "title": "Список занимающихся студентов",
                "name_button": "Исключить"
            }
            return render(request, "section/list.html", context=context)
    else:
        raise Http404

def deleteCoaches(request):
    if request.method == "POST":
        section_id = request.POST.get("section_id")
        if request.POST.get("button") == "button":
            item = Section.objects.get(id=section_id)
            for element in request.POST.getlist("arrayUserId"):
                user = User.objects.get(id=int(element))
                item.user_set.remove(user)
            return HttpResponsePermanentRedirect("section?Id=" + str(item.id))
        elif request.POST.get("button") == "sort":
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "section_id": section_id,
                "name_table": "Список тренеров секции",
                "title": "Список тренеров секции",
                "name_button": "Исключить"
            }
            if request.POST.get("criterion") == "surname":
                context["users"] = User.objects.filter(sections__id=section_id, role=2).order_by("surname")
            elif request.POST.get("criterion") == "name":
                context["users"] = User.objects.filter(sections__id=section_id, role=2).order_by("name")
            else:
                context["users"] = User.objects.filter(sections__id=section_id, role=2)
            return render(request, "section/list.html", context=context)
        else:
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "users": User.objects.filter(sections__id=section_id, role=2),
                "section_id": section_id,
                "name_table": "Список тренеров секции",
                "title": "Список тренеров секции",
                "name_button": "Исключить"
            }
            return render(request, "section/list.html", context=context)
    else:
        raise Http404

def listLessons(request):
    if request.method == "POST":
        if request.POST.get("button") == "add" and request.POST.get("year") and request.POST.get("month") and request.POST.get("day") and request.POST.get("year").isdigit() and request.POST.get("month").isdigit() and request.POST.get("day").isdigit():
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "section_id": request.POST.get("section_id"),
                "title": "Добавить занятие",
                "header": "Добавить занятие",
                "date": datetime.date(year=int(request.POST.get("year")), month=int(request.POST.get("month")),
                                      day=int(request.POST.get("day"))),
            }
            return render(request, "section/add-lesson.html", context=context)
        elif request.POST.get("button") == "delete":
            lessons_id = request.POST.getlist("lesson_id")
            for element in lessons_id:
                Lesson.objects.filter(id=int(element)).delete()
            return HttpResponsePermanentRedirect("list-lessons?Id=" + request.POST.get("section_id")
                                                 + "&year=" + request.POST.get("year") + "&month=" +
                                                 request.POST.get("month") + "&day=" + request.POST.get("day"))
        elif request.POST.get("button") == "sort" and request.POST.get("year") and request.POST.get("month") and request.POST.get("day") and request.POST.get("year").isdigit() and request.POST.get("month").isdigit() and request.POST.get("day").isdigit():
            section_id = request.POST.get("section_id")
            date = datetime.date(year=int(request.POST.get("year")), month=int(request.POST.get("month")),
                                 day=int(request.POST.get("day")))
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "date": date,
                "section_id": section_id,
            }
            if request.POST.get("criterion") == "start-time-increase":
                context["lessons"] = Lesson.objects.filter(date=date,
                                                           section=Section.objects.get(id=section_id)).order_by("start_time")
            elif request.POST.get("criterion") == "start-time-decrease":
                context["lessons"] = Lesson.objects.filter(date=date,
                                                           section=Section.objects.get(id=section_id)).order_by("-start_time")
            else:
                context["lessons"] = Lesson.objects.filter(date=date,
                                                           section=Section.objects.get(id=section_id))
            return render(request, "section/list-lessons.html", context=context)
        elif request.POST.get("button") == "back":
            return HttpResponsePermanentRedirect("section?Id=" + request.POST.get("section_id"))
        elif request.POST.get("edit") is not None and request.POST.get("year") and request.POST.get("month") and request.POST.get("day") and request.POST.get("year").isdigit() and request.POST.get("month").isdigit() and request.POST.get("day").isdigit():
            lesson_id = request.POST.get("edit")
            lesson = Lesson.objects.get(id=lesson_id)
            context = {
                "sections": Section.objects.all(),
                "section_id": request.POST.get("section_id"),
                "user": getUserFromSession(request),
                "lesson": lesson,
                "title": "Редактировать занятие",
                "header": "Редактировать занятие",
                "date": datetime.date(year=int(request.POST.get("year")), month=int(request.POST.get("month")),
                                      day=int(request.POST.get("day"))),
            }
            if lesson.start_time < datetime.time(10, 0, 0):
                print(123)
                context["fixed"] = True
            return render(request, "section/add-lesson.html", context=context)
        else:
            raise Http404
    else:
        Id = request.GET.get("Id")
        try:
            date = datetime.date(year=int(request.GET.get("year")), month=int(request.GET.get("month")),
                                 day=int(request.GET.get("day")))
            item = Section.objects.get(id=Id)
        except (ValueError, Section.DoesNotExist):
            raise Http404
        context = {
            "sections": Section.objects.all(),
            "user": getUserFromSession(request),
            "date": date,
            "section_id": Id,
            "lessons": Lesson.objects.filter(date=date, section=item),
        }
        return render(request, "section/list-lessons.html", context=context)

def addLesson(request):
    if request.method == "POST":
        lesson_form = LessonForm(request.POST)
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        day = int(request.POST.get("day"))
        Id = int(request.POST.get("section_id"))
        if request.POST.get("lesson_id") is not None:
            if lesson_form.is_valid():
                Lesson.objects.filter(id=request.POST.get("lesson_id")).update(**lesson_form.cleaned_data)
                return HttpResponsePermanentRedirect("list-lessons?Id=" + str(Id) + "&year=" + str(year) + "&month="
                                                     + str(month) + "&day=" + str(day))
            else:
                context = {
                    "sections": Section.objects.all(),
                    "user": getUserFromSession(request),
                    "section_id": Id,
                    "lesson": Lesson.objects.get(id=request.POST.get("lesson_id")),
                    "date": datetime.date(year=year, month=month,
                                          day=day),
                    "title": "Редактировать занятие",
                    "header": "Редактировать занятие",
                    "error": "Неправильный ввод данных",
                }
                return render(request, "section/add-lesson.html", context=context)
        else:
            if lesson_form.is_valid():
                lesson_form.cleaned_data["date"] = datetime.date(year=year, month=month, day=day)
                lesson_form.cleaned_data["coach"] = getUserFromSession(request)
                lesson_form.cleaned_data["section"] = Section.objects.get(id=Id)
                Lesson.objects.create(**lesson_form.cleaned_data)
                return HttpResponsePermanentRedirect("list-lessons?Id=" + str(Id) + "&year=" + str(year) + "&month="
                                                     + str(month) + "&day=" + str(day))
            else:
                context = {
                    "sections": Section.objects.all(),
                    "user": getUserFromSession(request),
                    "section_id": Id,
                    "date": datetime.date(year=year, month=month, day=day),
                    "title": "Добавить занятие",
                    "header": "Добавить занятие",
                    "error": "Неправильный ввод данных"
                }
                return render(request, "section/add-lesson.html", context=context)
    else:
        raise Http404

def detailed(request):
    section_id = request.GET.get("section_id")
    try:
        item = Section.objects.get(id=section_id)
    except Section.DoesNotExist:
        raise Http404
    context = {
        "sections": Section.objects.all(),
        "user": getUserFromSession(request),
        "section_id": section_id,
    }
    if request.GET.get("name") == "description":
        context["title"] = "О секции"
        context["header"] = "О секции"
        context["text"] = item.description
    elif request.GET.get("name") == "progress":
        context["title"] = "Достижения секции"
        context["header"] = "Достижения секции"
        context["text"] = item.progress
    elif request.GET.get("name") == "beginner":
        context["title"] = "Как записаться на секцию?"
        context["header"] = "Как записаться на секцию?"
        context["text"] = item.beginner
    else:
        raise Http404
    return render(request, "section/more-detailed.html", context=context)

# ----------------------Списки------------------------------------------------------- #

def listUsers(request):
    if request.method == "POST":
        if request.POST.get("button") == "delete":
            for element in request.POST.getlist("user_id"):
                User.objects.filter(id=int(element)).delete()
        elif request.POST.get("button") == "sort":
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
            }
            if request.POST.get("criterion") == "role-decrease":
                users = User.objects.exclude(role=1).order_by("role")
            elif request.POST.get("criterion") == "role-increase":
                users = User.objects.exclude(role=1).order_by("-role")
            else:
                users = User.objects.exclude(role=1)
            context["users"] = users
            return render(request, "lists/list-users.html", context=context)
        else:
            roles = request.POST.getlist("role")
            for i, element in enumerate(User.objects.exclude(role=1)):
                if int(roles[i]) != element.role:
                    element.role = roles[i]
                    element.save()
        return HttpResponsePermanentRedirect("list-users")
    else:
        adminRights(request)
        context = {
            "sections": Section.objects.all(),
            "user": getUserFromSession(request),
            "users": User.objects.exclude(role=1),
        }
        return render(request, "lists/list-users.html", context=context)

def listSections(request):
    if request.method == "POST":
        if request.POST.get("button") == "delete":
            for element in request.POST.getlist("section_id"):
                Section.objects.filter(id=int(element)).delete()
            return HttpResponsePermanentRedirect("list-sections")
        elif request.POST.get("button") == "add":
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "title": "Добавить секцию",
                "header": "Добавить секцию",
            }
            return render(request, "lists/edit-section.html", context=context)
        elif request.POST.get("edit") is not None:
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "title": "Редактировать секцию",
                "header": "Редактировать секцию",
                "section": Section.objects.get(id=request.POST.get("edit")),
            }
            return render(request, "lists/edit-section.html", context=context)
        else:
            raise Http404
    else:
        adminRights(request)
        return wideView(request, "lists/list-sections.html")

def addSection(request):
    if request.method == "POST":
        section_form = SectionForm(request.POST)
        if section_form.is_valid():
            if Section.objects.filter(name=section_form.cleaned_data["name"]).count() > 0:
                context = {
                    "sections": Section.objects.all(),
                    "user": getUserFromSession(request),
                    "title": "Добавить секцию",
                    "header": "Добавить секцию",
                    "error": "Такое название секции уже существует",
                }
                return render(request, "lists/edit-section.html", context=context)
            Section.objects.create(**section_form.cleaned_data)
            return HttpResponsePermanentRedirect("list-sections")
        else:
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "title": "Добавить секцию",
                "header": "Добавить секцию",
                "error": "Неправильный ввод данных",
            }
            return render(request, "lists/edit-section.html", context=context)
    else:
        raise Http404

def editSection(request):
    if request.method == "POST":
        section_form = SectionForm(request.POST)
        Id = request.POST.get("section_id")
        if section_form.is_valid():
            if Section.objects.filter(name=section_form.cleaned_data["name"]).exclude(id=Id).count() > 0:
                context = {
                    "sections": Section.objects.all(),
                    "user": getUserFromSession(request),
                    "title": "Редактировать секцию",
                    "header": "Редактировать секцию",
                    "section": Section.objects.get(id=Id),
                    "error": "Такое название секции уже существует",
                }
                return render(request, "lists/edit-section.html", context=context)
            Section.objects.filter(id=Id).update(**section_form.cleaned_data)
            return HttpResponsePermanentRedirect("list-sections")
        else:
            context = {
                "sections": Section.objects.all(),
                "user": getUserFromSession(request),
                "title": "Редактировать секцию",
                "header": "Редактировать секцию",
                "section": Section.objects.get(id=Id),
                "error": "Неправильный ввод данных",
            }
            return render(request, "lists/edit-section.html", context=context)
    else:
        raise Http404

# ----------------------Поиск-------------------------------------------------------- #

def search(request):
    if request.method == "POST" and request.POST.get("name") is not None:
        try:
            name = request.POST.get("name").replace(" ", "").title()
            if name == "Главная":
                return HttpResponsePermanentRedirect("/")
            elif name == "Профиль":
                return HttpResponsePermanentRedirect("profile")
            item = Section.objects.get(name=name)
            return HttpResponsePermanentRedirect("section?Id=" + str(item.id))
        except Section.DoesNotExist:
            return render(request, "error/error-search.html")
    else:
        raise Http404

# ----------------------------------------------------------------------------------- #