# ShowTrac

### Members: Margaret Rivas, Romail Khan, Hunter Yavorsky, Jacob McDuffie

### Project Description:
A platform to keep track of your TV Shows, Movies, and Anime. You can add shows to your list, rate them, and keep track of your progress.

### UI Instructions
Pretty straight forward and easy for new users.

### Libraries Used
- AnilistPython
- PyMovieDb
- Flask
- Pyrebase - Python Wrapper for Google Firebase Backend

### Extra Features
- Top Shows section that continuously pulls updated top 50 shows after a certain interval
- Search a show based on a critera for users to add - WIP

### Seperation of Work
- Margaret Rivas: Implemented ShowTrac+ section for TV Shows and Movies (included Movie API). Added user roles and banning. Added Upgrading to Premium Feature. Added Search By Criteria feature.
- Romail Khan: Login implementation. Database and Authentication. CRUD on Anime Section. Card UI Design.
- Hunter Yavorsky: Top Shows implementation and testing API. Also assisted in Front End
- Jacob McDuffie: Added Ratings on Each Anime/Show/Movie. Parallelization of Searching of Shows. Added change username.
    * To better the quality of the top 50 page, we wanted to add the shows ratings as well as a higher quality image for the poster. This would be achieved by pulling the IMDB listing for the show using the id given by the top 50 function. While each pull takes about 1-2 seconds, we would have to parallelize it to make it useable. This was ultimately not implemented due to the handling of the data being very complicated that finding where exactly to store the data and then retrieve it was giving us issues.


### Checklist:

**Security**
- [X] Use SSH keys for access into the server
- [ ] Use Nginx configuration tailored for security -- csrf, xss, etc.
- [X] Use role based access control for the database

**Distributed**
- [X] Separate script for getting top shows
- [ ] Use cron on web server to run script every day and add to database

**Premium Features**
- [X] Bring in API for show tracking
- [X] Add movie / show to user database
- [X] Add Search Bar that searches for the movie/show through the API 

**High Priority** 
- [X] Create database and add user information into it (firebase)
- [X] Show user data on the app page
- [X] Add anime to user database
- [X] Add Search Bar that searches for the anime through the API - Limited by the API (just adds instead of searching)
- [ ] Filter system to display specific anime cards

**Medium Priority**
- [X] Bring in API for anime tracking
- [ ] Add rating to the show - currently API controlled
- [X] Add status to the show (watching, completed, etc.)
- [X] Add delete button to cards

**Low Priority**
- [X] Log in and signup modals
- [X] Add a profile page
- [X] Add logout button / functionality    