document.addEventListener("DOMContentLoaded", () => {
    const monthDropdown = document.getElementById("monthDropdown");
    const moviesContainer = document.getElementById("moviesContainer");
    const loadingMessage = document.getElementById("loading-message");

    // Loading messages
    const messages = [
        "Preparing your recommendations...",
        "Fetching top genres...",
        "Retrieving movie posters..."
    ];
    let msgIndex = 0;
    let interval;

    function startLoading() {
        loadingMessage.style.display = "block";
        interval = setInterval(() => {
            loadingMessage.textContent = messages[msgIndex];
            msgIndex = (msgIndex + 1) % messages.length;
        }, 1500);
    }

    function stopLoading() {
        clearInterval(interval);
        loadingMessage.style.display = "none";
    }

    // Populate month dropdown
    const monthNames = [
        "January 2025","February 2025","March 2025","April 2025",
        "May 2025","June 2025","July 2025","August 2025",
        "September 2025","October 2025","November 2025","December 2025",
        "January 2026","February 2026"
    ];
    monthNames.forEach((name,i)=>{
        const option = document.createElement("option");
        option.value = i+1;
        option.textContent = name;
        monthDropdown.appendChild(option);
    });


    function showSkeletons(count = 8) {
        moviesContainer.innerHTML = ""; // clear previous
        for(let i = 0; i < count; i++) {
            const skeleton = document.createElement("div");
            skeleton.className = "skeleton-card";
            moviesContainer.appendChild(skeleton);
        }
    }

    async function fetchAndDisplay(url, isWatched=false, monthIndex=null){
        showSkeletons(); // show shimmering placeholders
        startLoading();
        try{
            const response = await fetch(url);
            const data = await response.json();
            let movies;

            if(isWatched){
                movies = monthIndex ? data[monthIndex] || [] : Object.values(data).flat();
                displayWatchedMovies(movies);
            } else {
                movies = data[monthIndex] || [];
                movies = movies.sort(()=>Math.random()-0.5).slice(0,8);
                displayMovies(movies);
            }
        } catch(err){
            moviesContainer.textContent = "Error loading movies.";
            console.error(err);
        } finally{
            stopLoading();
        }
    }

    // Display movie cards
    function displayMovies(movies){
        moviesContainer.innerHTML = ""; // remove skeletons

        if(!movies || movies.length === 0){
            // moviesContainer.textContent = "Not enough data to generate recommendations.";
            const card = document.createElement("div");
            card.className = "no-data-card";
            card.innerHTML = `
                <h3> Not Enough Data 😕</h3>
                <p>Sorry! There's not enough data to generate recommendations for this month.</p>
                <p>Try selecting another month!</p>
            `;
            moviesContainer.appendChild(card);
            return;
        }

        movies.forEach((movie, index) => {
            const card = document.createElement("div");
            card.className = "movie-card";

            card.innerHTML = `
                <div class="poster-wrapper">
                    <a href="${movie.letterboxdUri}" target="_blank" rel="noopener noreferrer">
                        <img src="${movie.poster}" alt="${movie.Name}">
                        <div class="poster-fallback">
                            <span>${movie.Name}</span>
                        </div>
                    </a>
                </div>
                <h4 class="movie-title">${movie.Name}</h4>
                <p>Genres: ${movie.genres.join(", ")}</p>
            `;

            const img = card.querySelector("img");
            const fallback = card.querySelector(".poster-fallback");

            img.onerror = () => showFallback(card.querySelector(".poster-wrapper"), movie.Name);

            moviesContainer.appendChild(card);

            // Animate with stagger
            setTimeout(() => {
                card.classList.add("show");
            }, index * 100);
        });
    }

    // Display watched movies list
    function displayWatchedMovies(movies){
        moviesContainer.innerHTML = "";
        if(!movies || movies.length === 0){
            moviesContainer.textContent = "No watched movies to display.";
            return;
        }

        movies.forEach((movie, index) => {
            const card = document.createElement("div");
            card.className = "watched-card";
            // optional: random pastel color for fun
            const pastel = `hsl(${Math.random()*360}, 70%, 30%)`;
            card.style.backgroundColor = pastel;

            card.textContent = movie.display; // movie title or display name
            moviesContainer.appendChild(card);

            // fade-in animation
            card.style.opacity = 0;
            setTimeout(() => {
                card.style.transition = "opacity 0.5s ease, transform 0.3s ease";
                card.style.opacity = 1;
                card.style.transform = "translateY(0)";
            }, index * 100);
        });
    }

    function showFallback(posterWrapper, movieName) {
        const fallback = posterWrapper.querySelector(".poster-fallback");
        const img = posterWrapper.querySelector("img");

        // Immediately hide broken image and show fallback
        img.style.display = "none";
        fallback.style.display = "flex";

        // Random background from your palette
        const colors = ["#00e054", "#ff8000", "#0099ff"]; // green, orange, blue
        fallback.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];

        // Set the movie title
        fallback.querySelector("span").textContent = movieName;
    }
    // Fetch JSON and display
    async function fetchAndDisplay(url, isWatched=false, monthIndex=null){
        startLoading();
        try{
            const response = await fetch(url);
            const data = await response.json();
            let movies;

            if(isWatched){
                movies = monthIndex ? data[monthIndex] || [] : Object.values(data).flat();
                displayWatchedMovies(movies);
            } else {
                movies = data[monthIndex] || [];
                movies = movies.sort(()=>Math.random()-0.5).slice(0,8);
                displayMovies(movies);
            }
        } catch(err){
            moviesContainer.textContent = "Error loading movies.";
            console.error(err);
        } finally{
            stopLoading();
        }
    }

    // Event listeners
    document.getElementById("getWatchedBtn").addEventListener("click", ()=>{
        const monthIndex = parseInt(monthDropdown.value) || null;
        fetchAndDisplay("watched.json", true, monthIndex);
    });

    document.getElementById("getRecommendationsBtn").addEventListener("click", ()=>{
        const monthIndex = parseInt(monthDropdown.value) || 1;
        fetchAndDisplay("recommendations.json", false, monthIndex);
    });

    // Load all watched movies by default
    // fetchAndDisplay("watched.json", true, null);
});