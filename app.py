import streamlit as st
import pickle 
import requests
import lzma

st.title("Movie Recommender System") 

movies_df = pickle.load(open('movies.pkl','rb'))#read binary mode
movies = movies_df['title'].values

with open('similarity.pkl.xz', 'rb') as f:  # Open in binary mode
    compressed_data = f.read()
similarity = pickle.loads(lzma.decompress(compressed_data))

selected_movie_name = st.selectbox('Movie Name:', movies)
number = st.slider('Number of Movies: ', 1, 50, 5)

def recommend(movie,number):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:number+1] #top 'number' movies
    recommended_movies = []
    recommended_movie_posters = []
    for i in movies_list:
        movie_id = movies_df.iloc[i[0]].id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movies.append(movies_df.iloc[i[0]].title)
    return recommended_movies,recommended_movie_posters

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=b5dce653bf9ad1272ab55ade0e0ced09&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data.get('poster_path')
    if poster_path is not None:
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        response = requests.get(full_path)
        if response.status_code == 200:
            return response.content  # Return poster image as bytes
    return None


if st.button('Show Recommendation'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie_name,number)

    for i in range(number):
        with st.container():
            st.markdown(f"**{recommended_movie_names[i]}**", unsafe_allow_html=True)#** for bolding the name of the movie
            if recommended_movie_posters[i] is not None:
                st.image(recommended_movie_posters[i],width=200)
                # st.caption(f"**{recommended_movie_names[i]}**")
                st.divider()
            else: 
                st.write("No poster available")
