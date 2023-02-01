from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import push, endpoint, customUser, batch
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import render
from django.core.files.storage import default_storage
from .tasks import batch_file
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .serializers import pushSerializer
from django.http import JsonResponse
from django.http import HttpResponse
import json
import stripe
import time
import uuid


def logIn(
    request,
):
    page = "login"
    context = {"page": page}

    if request.user.is_authenticated:
        return redirect("activity")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = customUser.objects.get(email=email)
        except:
            messages.error(request, "Incorrect email or password")
            return redirect("login")
        if user is not None:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            if user.check_password(password):
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Incorrect email or password")
                return redirect("login")
    return render(request, "datarocket/auth.html", context)


def signup(request):
    page = "signup"
    context = {"page": page}
    stripe.api_key = "sk_test_51MW7X8JK24mGyo15BLUr4Kws8xXkhVdUEosBvc72Dszieigba7tgVElf16itVudtT0hEW0EmIgtbMWY9KjJhB3Ij00YA88TsTf"

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        if password == password_confirm:
            if customUser.objects.filter(email=email).exists():
                messages.error(request, "Email address is invalid")
                return redirect("signup")
            else:
                user = customUser.objects.create_user(
                    username=email, email=email, password=password
                )
                user.backend = "django.contrib.auth.backends.ModelBackend"
                user.stripe_id = stripe.Customer.create(email=user.email).id
                user.save()
                login(request, user)
                return redirect("home")
        else:
            messages.error(request, "Your passwords do not match")
            return redirect("signup")

    return render(request, "datarocket/auth.html", context)


def signOut(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def activity(request):
    stripe.api_key = 'sk_test_51MW7X8JK24mGyo15BLUr4Kws8xXkhVdUEosBvc72Dszieigba7tgVElf16itVudtT0hEW0EmIgtbMWY9KjJhB3Ij00YA88TsTf'
    user = request.user
    if user.stripe_plan_id != None:
     plan = stripe.Price.retrieve(user.stripe_plan_id).nickname
    endpoints = endpoint.objects.filter(user=user)
    page = "home"
    user = request.user
    pushes = push.objects.filter(user=user).order_by("-created")[:5]
    for p in pushes:
        p.endpoint = endpoint.objects.get(id=p.endpoint_id)
        p.completed = batch.objects.filter(push=p, completed=True).count()
        p.total = batch.objects.filter(push=p).count()
        if p.completed != 0 and p.total != 0:
            p.percent = round((p.completed / p.total) * 100, 2)
    context = {"pushes": pushes, "page": page, "endpoints": endpoints, "plan": plan}
    return render(request, "datarocket/activity.html", context) 


@login_required(login_url="login")
def pushes(request):
    user = request.user
    page = "launches"
    filter = request.GET.get("filter")
    sort = request.GET.get("sort")
    endpoints = endpoint.objects.filter(user=user)
    for e in endpoints:
        e.str = str(e.id)
    if filter != None:
        try:
            pushes = push.objects.filter(user=user, endpoint=filter).order_by("-created")
        except:
            pushes = push.objects.filter(user=user).order_by("-created")
    else:
        pushes = push.objects.filter(user=user).order_by("-created")
    for p in pushes:
        if p.status == "Complete":
            last_batch = batch.objects.filter(push=p, completed=True).order_by("-created").first()
            time = last_batch.finished - p.created
            p.time = round(time.seconds/60, 2)
        p.endpoint = endpoint.objects.get(id=p.endpoint_id)
        p.total = batch.objects.filter(push=p).count()
        p.completed = batch.objects.filter(push=p, completed=True, failed=False).count()
        p.failed = batch.objects.filter(push=p, failed=True).count()
        if p.status == "Complete":
            p.rate = (p.completed / p.total)*100
        if p.completed != 0 and p.total != 0:
            p.percent = round((p.completed / p.total) * 100, 2)
    context = {"pushes": pushes, "page": page, "endpoints": endpoints, "filter": filter, "sort": sort}
    return render(request, "datarocket/pushes.html", context)


@login_required(login_url="login")
def endpoints(request):
    user = request.user
    page = "endpoints"
    endpoints = endpoint.objects.filter(user=user)
    for e in endpoints:
        e.pushes = push.objects.filter(endpoint=e).count()
    context = {"endpoints": endpoints, "page": page}
    return render(request, "datarocket/endpoints.html", context)


# Functions to create, delete and update pushes and endpoints


@login_required(login_url="login")
def createPush(request, page):
    user = request.user
    if request.method == "POST":
        description = request.POST.get("description")
        endpoint_id = request.POST.get("endpoint")
        json_file = request.FILES["json"]
        workers = request.POST.get("workers")
        fs = FileSystemStorage()
        file = fs.save(str(uuid.uuid4()) + ".json", json_file)
        p = push(
            user=user,
            description=description,
            json_file=file,
            endpoint=endpoint.objects.get(id=endpoint_id),
            status="Queued",
            workers=workers,
        )
        p.save()
        batch_file(p)
        return redirect(page)


@login_required(login_url="login")
def createEndpoint(request, page):
    user = request.user
    if request.method == "POST":
        description = request.POST.get("description")
        url = request.POST.get("url")
        e = endpoint(user=user, description=description, url=url)
        e.save()
    return redirect(page)


@login_required(login_url="login")
def deletePush(request, id):
    if request.method == "GET":
        push.objects.filter(id=id).delete()
    return redirect("launches")


@login_required(login_url="login")
def deleteEndpoint(request, id):
    if request.method == "GET":
        endpoint.objects.filter(id=id).delete()
    return redirect("endpoints")

@login_required(login_url="login")
def stripe_checkout(request):
    stripe.api_key = 'sk_test_51MW7X8JK24mGyo15BLUr4Kws8xXkhVdUEosBvc72Dszieigba7tgVElf16itVudtT0hEW0EmIgtbMWY9KjJhB3Ij00YA88TsTf'
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                'price': 'price_1MWAMaJK24mGyo15WjgYhv5L',
                'quantity': 1,
            },
        ],
        mode='subscription',
        customer=request.user.stripe_id,
        success_url='https://app.datarocket.app' + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://app.datarocket.app',
    )
    return redirect(checkout_session.url, code=303)
    
@login_required(login_url="login")
def create_portal_session(request):
    user = request.user
    portalSession = stripe.billing_portal.Session.create(
        customer=user.stripe_id,
        return_url="https://app.datarocket.app",
    )
    return redirect(portalSession.url, code=303)

@csrf_exempt
def stripe_webhook(request):
    if request.method == "POST":
        body = json.loads(request.body)
        if body['type'] == 'customer.subscription.created' or body['type'] == 'customer.subscription.updated':
            customer = body['data']['object']['customer']
            user = customUser.objects.get(stripe_id=customer)
            user.stripe_plan_active = True
            user.stripe_subscription_id = body['data']['object']['id']
            user.stripe_plan_id = body['data']['object']['items']['data'][0]['price']['id']
            user.save()
        else:
            print('Unhandled event type {}'.format(body['type']))

        return HttpResponse(status=200)

    
    

    