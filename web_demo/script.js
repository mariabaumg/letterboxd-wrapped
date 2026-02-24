document.addEventListener("DOMContentLoaded", () => {
    const monthDropdown = document.getElementById("monthDropdown");
    const moviesContainer = document.getElementById("moviesContainer");
    const loadingSpinner = document.getElementById("loading");

    // ----------------------------
    // Populate month dropdown
    // ----------------------------
    const monthNames = [
        "January 2025", "February 2025", "March 2025", "April 2025",
        "May 2025", "June 2025", "July 2025", "August 2025",
        "September 2025", "October 2025", "November 2025", "December 2025",
        "January 2026", "February 2026"
    ];
    monthNames.forEach((name, i) => {
        const option = document.createElement("option");
        option.value = i + 1;
        option.textContent = name;
        monthDropdown.appendChild(option);
    });

    // ----------------------------
    // Display movies (recommendations)
    // ----------------------------
    function displayMovies(movies) {
        moviesContainer.innerHTML = "";
        if (!movies || movies.length === 0) {
            moviesContainer.textContent = "No movies to display.";
            return;
        }

        movies.forEach(movie => {
            const card = document.createElement("div");
            card.className = "movie-card";
            card.innerHTML = `
                <img src="${movie.poster}" alt="${movie.Name || movie.name}" style="width:150px;height:225px"/>
                <h4>${movie.Name || movie.name}</h4>
                <p>Genres: ${movie.genres ? movie.genres.join(", ") : "N/A"}</p>
                <p>Rating: ${movie.rating || "N/A"}</p>
            `;
            moviesContainer.appendChild(card);
        });
    }

    // ----------------------------
    // Display watched movies (simple list)
    // ----------------------------
    function displayWatchedMovies(movies) {
        moviesContainer.innerHTML = "";
        if (!movies || movies.length === 0) {
            moviesContainer.textContent = "No watched movies to display.";
            return;
        }

        const ul = document.createElement("ul");
        ul.className = "watched-list";

        movies.forEach(movie => {
            const li = document.createElement("li");
            li.textContent = movie.display; // "Movie Name (Year)"
            ul.appendChild(li);
        });

        moviesContainer.appendChild(ul);
    }

    // ----------------------------
    // Fetch data and display
    // ----------------------------
    async function fetchAndDisplay(url, payload, isWatched = false) {
        moviesContainer.innerHTML = "";
        loadingSpinner.style.display = "block";

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const movies = await response.json();
            if (isWatched) {
                displayWatchedMovies(movies);
            } else {
                displayMovies(movies);
            }
        } catch (err) {
            moviesContainer.textContent = "Error loading movies.";
            console.error(err);
        } finally {
            loadingSpinner.style.display = "none";
        }
    }

    // ----------------------------
    // Event listeners
    // ----------------------------
    document.getElementById("getWatchedBtn").addEventListener("click", () => {
        const monthIndex = parseInt(monthDropdown.value) || null;
        fetchAndDisplay("/watched", { month_index: monthIndex }, true);
    });

    document.getElementById("getRecommendationsBtn").addEventListener("click", () => {
        const monthIndex = parseInt(monthDropdown.value) || null;
        fetchAndDisplay("/recommend", { month_index: monthIndex }, false);
    });

    // Load watched movies by default (all months)
    fetchAndDisplay("/watched", { month_index: null }, true);
});