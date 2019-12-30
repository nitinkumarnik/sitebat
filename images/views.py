from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from actions.utils import create_action
from common.decorators import ajax_required

from .forms import ImageCreateForm
from .models import Image


@login_required
def image_create(request):
	if request.method == 'POST':
		form = ImageCreateForm(data=request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			new_item = form.save(commit=False)

			new_item.user = request.user
			new_item.save()
			create_action(request.user, 'bookmarked image', new_item)
			messages.success(request, 'Image added successfully.')
			return redirect(new_item.get_absolute_url())
	else:
		form = ImageCreateForm(data=request.GET)

	return render(request, 'create.html', {'section': 'images', 'form': form})


def image_detail(request, id, slug):
	image = get_object_or_404(Image, id=id, slug=slug)
	return render(request, 'detail.html', {'section': 'images', 'image': image})


@ajax_required
@login_required
@require_POST
def image_like(request):
	image_id = request.POST.get('id')
	action = request.POST.get('action')
	if image_id and action:
		try:
			image = Image.objects.get(id=image_id)
			if action == 'like':
				image.users_like.add(request.user)
				create_action(request.user, 'likes', image)
			else:
				image.users_like.remove(request.user)
			return JsonResponse({'status': 'ok'})
		except:
			pass
	return JsonResponse({'status': 'ko'})


@login_required
def image_list(request):
	images = Image.objects.all()
	paginator = Paginator(images, 8)
	page = request.GET.get('page')

	try:
		images = paginator.page(page)
	except PageNotAnInteger:
		images = paginator.page(1)
	except EmptyPage:
		if request.is_ajax():
			return HttpResponse('')
		images = paginator.page(paginator.num_pages)
	context = {'section': 'images', 'images': images}
	if request.is_ajax():
		return render(request, 'list_ajax.html', context)
	return render(request, 'list.html', context)