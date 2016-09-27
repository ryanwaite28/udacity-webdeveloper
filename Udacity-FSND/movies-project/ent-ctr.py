import builder
import movies

friday = movies.Movie("Friday",
"A Turn of Events Taking Place, All on a Friday.",
"http://static.comicvine.com/uploads/original/11118/111180200/4547263-9728807078-Frida.jpg",
"https://www.youtube.com/watch?v=dxduMVVnrvU")

scary_movie_two = movies.Movie("Scary Movie 2",
"Group of Young Adults are Trapped in a Haunted Mansion and Must Figure Out a Means of Escape.",
"http://img.hindilinks4u.to/2014/11/Scary-Movie-2-2001-In-Hindi.jpg",
"https://www.youtube.com/watch?v=zCFZUZxBVuI")

butterfly_effect = movies.Movie("The Butterfly Effect",
"A Boy, With the Ability to Go Back in Time and Redo History, Tries to Create the Best Outcome.",
"https://fanart.tv/api/download.php?type=download&image=50578&section=3",
"https://www.youtube.com/watch?v=g5FFh8PH0mY")

mean_girls = movies.Movie("Mean Girls",
"A Transfer Student Coming from Africa Enters The Monstrous World of High School.",
"http://media4.popsugar-assets.com/files/2014/10/14/907/n/1922283/374fb51479b4858d_mean_girls_movie_poster_wallpaper_hd_for_desktop/i/Mean-Girls.jpg",
"https://www.youtube.com/watch?v=KAOmTMCtGkI")

jumanji = movies.Movie("Jumanji",
"A Gameboard With Evil Magic Causes Horror and Won't Stop Until the Game is Over.",
"http://ecx.images-amazon.com/images/I/91MTunoIa5L._SL1500_.jpg",
"https://www.youtube.com/watch?v=OJKHQLM8AbM")

district_nine = movies.Movie("District 9",
"Aliens, That Are Trapped on Earth, Tries to Find a Way Back Home.",
"http://images.moviepostershop.com/district-9-movie-poster-2009-1020502468.jpg",
"https://www.youtube.com/watch?v=DyLUwOcR5pk")

movies = [friday, scary_movie_two, butterfly_effect, mean_girls, jumanji, district_nine]
builder.open_movies_page(movies)
