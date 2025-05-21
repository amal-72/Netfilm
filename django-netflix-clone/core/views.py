from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Movie, MovieList, Section, Profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import re

# Create your views here.
@login_required(login_url='login')
def index(request):
    # Vérifier si un profil est sélectionné
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('profile_selection')
        
    try:
        current_profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('profile_selection')

    movies = Movie.objects.all()
    featured_movie = movies.last()
    sections = Section.objects.filter(is_active=True).order_by('order')

    context = {
        'movies': movies,
        'featured_movie': featured_movie,
        'sections': sections,
        'current_profile': current_profile
    }
    return render(request, 'index.html', context)

@login_required(login_url='login')
def movie(request, pk):
    # Vérifier si un profil est sélectionné
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('profile_selection')
        
    try:
        current_profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('profile_selection')
        
    movie_uuid = pk
    movie_details = Movie.objects.get(uu_id=movie_uuid)

    context = {
        'movie_details': movie_details,
        'current_profile': current_profile
    }

    return render(request, 'movie.html', context)

@login_required(login_url='login')
def genre(request, pk):
    # Vérifier si un profil est sélectionné
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('profile_selection')
        
    try:
        current_profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('profile_selection')
        
    movie_genre = pk
    movies = Movie.objects.filter(genre=movie_genre)
    
    # Obtenir le nom du genre en français
    genre_name = dict(Movie.GENRE_CHOICES).get(movie_genre, movie_genre.capitalize())

    context = {
        'movies': movies,
        'movie_genre': movie_genre,
        'genre_name': genre_name,
        'current_profile': current_profile
    }
    return render(request, 'genre.html', context)

@login_required(login_url='login')
def search(request):
    # Vérifier si un profil est sélectionné
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('profile_selection')
        
    try:
        current_profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('profile_selection')
        
    if request.method == 'POST':
        search_term = request.POST['search_term']
        movies = Movie.objects.filter(title__icontains=search_term)

        context = {
            'movies': movies,
            'search_term': search_term,
            'current_profile': current_profile
        }
        return render(request, 'search.html', context)
    else:
        return redirect('/')

@login_required(login_url='login')
def my_list(request):
    # Vérifier si un profil est sélectionné
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('profile_selection')
        
    try:
        current_profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('profile_selection')

    movie_list = MovieList.objects.filter(owner_user=request.user)
    user_movie_list = []

    for movie in movie_list:
        user_movie_list.append(movie.movie)

    context = {
        'movies': user_movie_list,
        'current_profile': current_profile
    }
    return render(request, 'my_list.html', context)

@login_required(login_url='login')
def add_to_list(request):
    if request.method == 'POST':
        try:
            movie_id = request.POST.get('movie_id')
            if not movie_id:
                return JsonResponse({'status': 'error', 'message': 'Movie ID is required'}, status=400)
                
            movie = Movie.objects.get(uu_id=movie_id)
            movie_list, created = MovieList.objects.get_or_create(owner_user=request.user, movie=movie)

            if created:
                return JsonResponse({'status': 'success', 'message': 'Added to My List'})
            else:
                return JsonResponse({'status': 'info', 'message': 'Movie already in list'})
                
        except Movie.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Movie not found'}, status=404)
        except Exception as e:
            print(f"Error in add_to_list: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required(login_url='login')
def remove_from_list(request):
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        movie = get_object_or_404(Movie, uu_id=movie_id)
        movie_list = MovieList.objects.filter(owner_user=request.user, movie=movie)
        
        if movie_list.exists():
            movie_list.delete()
            return JsonResponse({'status': 'success', 'message': 'Removed from list'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Movie not in list'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            # Vérifier si l'utilisateur a des profils
            if Profile.objects.filter(user=user).exists():
                return redirect('profile_selection')
            else:
                # Si pas de profils, créer un profil par défaut
                Profile.objects.create(
                    user=user,
                    name=user.username,
                    is_child=False
                )
                return redirect('profile_selection')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')
    
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                try:
                    # Créer l'utilisateur
                    user = User.objects.create_user(username=username, email=email, password=password)
                    user.save()

                    # Connecter l'utilisateur
                    user_login = auth.authenticate(username=username, password=password)
                    auth.login(request, user_login)
                    
                    # Créer un profil par défaut avec un nom unique
                    profile_name = f"{username}'s Profile"
                    Profile.objects.create(
                        user=user_login,
                        name=profile_name,
                        is_child=False
                    )
                    
                    return redirect('profile_selection')
                except Exception as e:
                    # En cas d'erreur, supprimer l'utilisateur créé
                    if user:
                        user.delete()
                    messages.info(request, str(e))
                    return redirect('signup')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile_selection(request):
    profiles = Profile.objects.filter(user=request.user)
    can_create = profiles.count() < 4  # Maximum 4 profiles per user
    
    context = {
        'profiles': profiles,
        'can_create': can_create
    }
    return render(request, 'profile_selection.html', context)

@login_required(login_url='login')
def create_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        is_child = request.POST.get('is_child', '') == 'on'
        image = request.FILES.get('image')
        
        # Vérifier si un profil avec ce nom existe déjà pour cet utilisateur
        if Profile.objects.filter(user=request.user, name=name).exists():
            messages.error(request, 'Un profil avec ce nom existe déjà')
            return render(request, 'create_profile.html')
        
        if Profile.objects.filter(user=request.user).count() >= 4:
            messages.error(request, 'Maximum number of profiles reached')
            return redirect('profile_selection')
        
        profile = Profile.objects.create(
            user=request.user,
            name=name,
            is_child=is_child
        )
        if image:
            profile.image = image
            profile.save()
            
        return redirect('profile_selection')
    
    return render(request, 'create_profile.html')

@login_required(login_url='login')
def edit_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        is_child = request.POST.get('is_child', '') == 'on'
        image = request.FILES.get('image')
        
        profile.name = name
        profile.is_child = is_child
        if image:
            profile.image = image
        profile.save()
        
        return redirect('profile_selection')
    
    context = {
        'profile': profile
    }
    return render(request, 'edit_profile.html', context)

@login_required(login_url='login')
def delete_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    
    if request.method == 'POST':
        profile.delete()
        return redirect('profile_selection')
    
    context = {
        'profile': profile
    }
    return render(request, 'delete_profile.html', context)

@login_required(login_url='login')
def select_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    request.session['profile_id'] = profile.id
    return redirect('index')

@login_required(login_url='login')
def movie_details(request, pk):
    movie = get_object_or_404(Movie, uu_id=pk)
    data = {
        'title': movie.title,
        'description': movie.description,
        'release_date': movie.release_date.strftime('%Y-%m-%d'),
        'genre': movie.get_genre_display(),
        'length': movie.length,
        'movie_views': movie.movie_views,
        'image_cover': movie.image_cover.url,
    }
    return JsonResponse(data)

@login_required(login_url='login')
def update_profile_image(request, profile_id):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            profile = get_object_or_404(Profile, id=profile_id, user=request.user)
            profile.image = request.FILES['image']
            profile.save()
            
            # Update current profile in session if it's the same
            if request.session.get('profile_id') == profile_id:
                request.session['profile_id'] = profile_id
                
            return JsonResponse({
                'success': True,
                'image_url': profile.image.url,
                'message': 'Profile image updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    }, status=400)

@login_required(login_url='login')
def all_genres(request):
    # Vérifier si un profil est sélectionné
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return redirect('profile_selection')
        
    try:
        current_profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist:
        return redirect('profile_selection')

    # Récupérer les choix de genres à partir du modèle Movie
    genres = dict(Movie.GENRE_CHOICES)
    
    # Compter le nombre de films dans chaque genre
    genre_counts = {}
    for genre_key, genre_name in genres.items():
        count = Movie.objects.filter(genre=genre_key).count()
        genre_counts[genre_key] = {
            'name': genre_name,
            'count': count
        }
    
    context = {
        'genres': genre_counts,
        'current_profile': current_profile
    }
    return render(request, 'all_genres.html', context)