var films = new Bloodhound({
    datumTokenizer: function (datum) {
        return Bloodhound.tokenizers.whitespace(datum.value);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    limit: 10,
    remote: {
        url: 'http://127.0.0.1:5000/films?query=%QUERY',
        // url: 'http://api.themoviedb.org/3/search/movie?api_key=634014fb344524ac652cddca6c0b6442&query=%QUERY&search_type=ngram',
        filter: function (films) {
            // Map the remote source JSON array to a JavaScript array
            return $.map(films, function (film) {
                return {
                    id: film.film_id,
                    value: film.film_title
//                    year: (film.release_date.substr(0, 4) ? film.release_date.substr(0, 4) : ''),
//                    poster: film.poster_path,
//                    budget: film.budget,
//                    revenue: film.revenue,
//                    runtime: film.runtime,
//                    release_date: film.release_date,
//                    vote_average: film.vote_average,
//                    overview: film.overview
                };
            });
        }
    }
});

// Initialize the Bloodhound suggestion engine
films.initialize();

// Instantiate the Typeahead UI
$('.typeahead').typeahead({
    hint: true,
    highlight: true,
	minLength: 2
}, {
    displayKey: 'value',
    source: films.ttAdapter(),
    templates: {
        empty: [
            '<div class="empty-message">',
            'Unable to find any films that match the current query.',
            '</div>'].join('\n'),
        suggestion: Handlebars.compile('<p><strong>{{value}}</strong></p>')
    }
}).on('typeahead:selected', function (obj, datum) {
$.getJSON('http://127.0.0.1:5000/films/' + datum.id, function(data) {
    $('.typeahead').typeahead('val', '');

    document.getElementById('film_title').innerHTML = data.film_title;
    document.getElementById('film_poster').src = data.film_poster_url.replace("w640", "w1280");
    document.getElementById('film_vote_average').innerHTML = data.film_vote_average * 10 + "%";
    document.getElementById('film_overview').innerHTML = data.film_overview;
    document.getElementById('film_runtime').innerHTML = data.film_runtime;
    document.getElementById('film_budget').innerHTML = "$" + data.film_budget;
    document.getElementById('film_revenue').innerHTML = "$" + data.film_revenue;
});
$.getJSON('http://api.themoviedb.org/3/movie/' + datum.id + '?api_key=634014fb344524ac652cddca6c0b6442', function(data2) {
    // var backdrop = "https://image.tmdb.org/t/p/w1280" + data2.backdrop_path;
    // $('#film_backdrop').css('background-image', 'url(https://image.tmdb.org/t/p/w1280' + data2.backdrop_path + ')');
    // document.getElementById("film_backdrop").style.backgroundImage = 'url(https://image.tmdb.org/t/p/w1280' + data2.backdrop_path + ')';
});
});