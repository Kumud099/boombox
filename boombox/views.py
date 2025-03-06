from django.shortcuts import render
from boombox.models import Song, Watchlater, History, Channel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.db.models import Case, When
from django.contrib.auth import authenticate, login as auth_login  

def search(request):
    query = request.GET.get("query", "").strip()  # Ensure it's a string and remove spaces
    
    if not query:  # If query is empty, return all songs or an error message
        return render(request, 'boombox/search.html', {"songs": [], "message": "No search query provided."})

    qs = Song.objects.filter(name__icontains=query)  # Case-insensitive search

    return render(request, 'boombox/search.html', {"songs": qs})



def history(request):
    if request.method == "POST":
        user = request.user
        music_id = request.POST['music_id']
        history = History(user=user, music_id=music_id)
        history.save()

        return redirect(f"/boombox/songs/{music_id}")

    history = History.objects.filter(user=request.user)
    ids = []
    for i in history:
        ids.append(i.music_id)
    
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, 'boombox/history.html', {"history": song})

def watchlater(request):
    if request.method == "POST":
        user = request.user
        video_id = request.POST['video_id']

        watch = Watchlater.objects.filter(user=user)
        
        for i in watch:
            if video_id == i.video_id:
                message = "Your Video is Already Added"
                break
        else:
            watchlater = Watchlater(user=user, video_id=video_id)
            watchlater.save()
            message = "Your Video is Succesfully Added"

        song = Song.objects.filter(song_id=video_id).first()
        return render(request, f"boombox/songpost.html", {'song': song, "message": message})

    wl = Watchlater.objects.filter(user=request.user)
    ids = []
    for i in wl:
        ids.append(i.video_id)
    
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, "boombox/watchlater.html", {'song': song})

def songs(request):
    song = Song.objects.all()
    return render(request, 'boombox/songs.html', {'song': song})

def songpost(request, id):
    song = Song.objects.filter(song_id=id).first()
    return render(request, 'boombox/songpost.html', {'song': song})

def login(request):  # Keeping your function name as `login`
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Use `auth_login` instead of `login`
            return redirect("/")
        else:
            return render(request, 'boombox/login.html', {"error": "Invalid username or password"})

    return render(request, 'boombox/login.html')



def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # if User.objects.filter(username=username).exists():
        #     messages.error(request, "Username is already taken. Please try another one !")
        #     return redirect("/")

        # if len(username) > 15:
        #     messages.error(request, "Username must be less than 15 characters")
        #     return redirect("/")
        
        # if not username.isalnum():
        #     messages.error(request, "Username should only contain Letters and Numbers.")

        # if pass1 != pass2:
        #     messages.error(request, "Password Do not Match. Please Sign Up Again")
        #     return redirect("/")


            
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.save()
        user = authenticate(username=username, password=pass1)
        from django.contrib.auth import login
        login(request, user)

        channel = Channel(name=username)
        channel.save()

        return redirect('/')

    return render(request, 'boombox/signup.html')

def logout_user(request):
    logout(request)
    return redirect("/")

def channel(request, channel):
    chan = Channel.objects.filter(name=channel).first()
    video_ids = str(chan.music).split(" ")[1:]

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(video_ids)])
    song = Song.objects.filter(song_id__in=video_ids).order_by(preserved)    

    return render(request, "boombox/channel.html", {"channel": chan, "song": song})

def upload(request):
    if request.method == "POST":
        name = request.POST['name']
        singer = request.POST['singer']
        
        image = request.FILES.get('image', None)  # ✅ Correct way to handle image files
        movie = request.POST['movie']
        song1 = request.FILES.get('file', None)  # ✅ Handle song files correctly

        song_model = Song(name=name, singer=singer, image=image, movie=movie, song=song1)
        song_model.save()


        music_id = song_model.song_id
        channel_find = Channel.objects.filter(name=str(request.user))
        print(channel_find)

        for i in channel_find:
            i.music += f" {music_id}"
            i.save()

    return render(request, "boombox/upload.html")
