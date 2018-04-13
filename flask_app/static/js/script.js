var films = new Bloodhound({
    datumTokenizer: function (datum) {
        return Bloodhound.tokenizers.whitespace(datum.value);
    },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    limit: 10,
    remote: {
        url: 'http://ksmall.me/films?query=%QUERY',
        // url: 'http://127.0.0.1:5000/films?query=%QUERY', // Local development only
        // url: 'http://api.themoviedb.org/3/search/movie?api_key=634014fb344524ac652cddca6c0b6442&query=%QUERY&search_type=ngram',
        filter: function (films) {
            // Map the remote source JSON array to a JavaScript array
            return $.map(films, function (film) {
                return {
                    id: film.film_id,
                    title: film.film_title,
					year: (film.film_release_date != null ? film.film_release_date.substr(0,4) : 'N/A')
                };
            });
        }
    }
});

// Initialize the Bloodhound suggestion engine
films.initialize();

var user_rating_bar = new ProgressBar.Line(user_rating_container, {
	strokeWidth: 2,
	easing: 'easeInOut',
	duration: 1400,
	color: '#81CFE0',
	trailColor: '#eee',
	trailWidth: 1,
	svgStyle: {width: '100%', height: '100%'},
	text: {
		style: {
			// Text color.
			// Default: same as stroke color (options.color)
			color: '#000',
			right: '0',
			position: 'absolute',
			top: '0px',
			padding: 0,
			margin: 0,
			transform: null
		},
		autoStyleContainer: false
	},
	from: {color: '#FFEA82'},
	to: {color: '#ED6A5A'},
	step: (state, bar) => {
		bar.setText(Math.round(bar.value() * 100) + ' %');
	}
});

var predicted_rating_bar = new ProgressBar.Line(predicted_rating_container, {
	strokeWidth: 2,
	easing: 'easeInOut',
	duration: 1400,
	color: '#81CFE0',
	trailColor: '#eee',
	trailWidth: 1,
	svgStyle: {width: '100%', height: '100%'},
	text: {
		style: {
			// Text color.
			// Default: same as stroke color (options.color)
			color: '#000',
			right: '0',
			position: 'absolute',
			top: '0px',
			padding: 0,
			margin: 0,
			transform: null
		},
		autoStyleContainer: false
	},
	from: {color: '#81CFE0'},
	to: {color: '#ED6A5A'},
	step: (state, bar) => {
		bar.setText(Math.round(bar.value() * 100) + ' %');
	}
});

function grabFilmData(film_id) {
	$.getJSON('http://ksmall.me/films/' + film_id, function(data) {
        $('.typeahead').typeahead('val', '');
    
        document.getElementById('film_title').innerHTML = data.film_title + (data.film_release_date != null ? "<span id=\"film_release_date_title\"> (" + data.film_release_date.substr(0,4) + ")</span>" : "") + (data.film_tagline != null ? "<p id=\"film_tagline\">" + data.film_tagline + "</p>" : "");
		
		if (data.film_poster_url == null) {
			document.getElementById('film_poster').src = "https://i.imgur.com/GMTSI1w.png";
		} else {
			document.getElementById('film_poster').src = data.film_poster_url;
		}

		user_rating_bar.animate(data.film_vote_average / 10);
		predicted_rating_bar.animate(data.film_prediction_rating / 100);
		
        // document.getElementById('film_vote_average').innerHTML = data.film_vote_average * 10 + "%";
        // document.getElementById('film_predicted_average').innerHTML = data.film_prediction_rating + "%";
		
        document.getElementById('film_overview').innerHTML = data.film_overview;
        document.getElementById('film_release_date').innerHTML = (data.film_release_date != null ? moment(data.film_release_date).format('MMMM Do YYYY') : '-');
		
		// Format the film runtimes
		var hours = parseInt(data.film_runtime / 60);
		var mins = data.film_runtime % 60;
		var duration;
		if (hours == 1) {
			duration = hours + "hr " + mins + "mins";
		} else if (hours < 1 && hours > 0) {
			duration = mins + "mins";
		} else if (hours == 0) {
			duration = "-"
		} else {
			duration = hours + "hrs " + mins + "mins";
		}
        document.getElementById('film_runtime').innerHTML = duration;
		
        document.getElementById('film_budget').innerHTML = currency(data.film_budget, { formatWithSymbol: true }).format();
        document.getElementById('film_revenue').innerHTML = currency(data.film_revenue, { formatWithSymbol: true }).format();
		
		// Show or hide the film trailer element
		if (data.film_trailer_url == null) {
			document.getElementById('film_trailer_heading').style.display = "none";
			document.getElementById('film_trailer').src = "";
			document.getElementById('film_trailer').style.display = "none";
		} else {
			document.getElementById('film_trailer_heading').style.display = "block";
			document.getElementById('film_trailer').style.display = "block";
			document.getElementById('film_trailer').src = data.film_trailer_url;
		}
		
		// Loop through and display genres
		$('#film_genres').empty();
		
		if (data.genres.length == 0) {
			$('#film_genres').append('<li>-</li>');
		} else {
			for (i = 0; i < data.genres.length; i++) {
				$('#film_genres').append('<li>' + data.genres[i]['genre_name'] + '</li>');
			}
		}
		
		// Loop through and display actors
		$('#film_actors').empty();
		
		if (data.actors.length == 0) {
			document.getElementById('film_actors_heading').style.display = "none";
			document.getElementById('film_actors').style.display = "none";
		} else {
			document.getElementById('film_actors_heading').style.display = "flex";
			document.getElementById('film_actors').style.display = "flex";
			
			for (i = 0; i < 5; i++) {
				$('#film_actors').append('<li>' + "<img src=\"" + (data.actors[i]['actor_pic_url'] != null ? data.actors[i]['actor_pic_url'] : "https://i.imgur.com/kpIG4or.png") + "\" />" + "<p class=\"actor_name\">" + data.actors[i]['actor_name'] + "</p>" + "<p class=\"actor_character\">" + data.actors[i]['actor_character'] + "</p>" + '</li>');
			}
		}
    });
}

// Grab initial film on page load
$(function(){
	grabFilmData(27205);
});

// Instantiate the Typeahead UI
$('.typeahead').typeahead({
    hint: true,
    highlight: true,
	minLength: 2
}, {
    displayKey: 'title',
    source: films.ttAdapter(),
    templates: {
        empty: [
            '<div class="empty-message">',
            'Unable to find any films that match the current query.',
            '</div>'].join('\n'),
        suggestion: Handlebars.compile('<p><strong>{{title}}</strong> – {{year}}</p>')
    }
}).on('typeahead:selected', function (obj, datum) {
    
	grabFilmData(datum.id);
	$('.navbar-collapse').collapse('hide'); // Trigger menu collapse
	
    // $.getJSON('http://api.themoviedb.org/3/movie/' + datum.id + '?api_key=634014fb344524ac652cddca6c0b6442', function(data2) {
        // var backdrop = "https://image.tmdb.org/t/p/w1280" + data2.backdrop_path;
        // $('#film_backdrop').css('background-image', 'url(https://image.tmdb.org/t/p/w1280' + data2.backdrop_path + ')');
        // document.getElementById("film_backdrop").style.backgroundImage = 'url(https://image.tmdb.org/t/p/w1280' + data2.backdrop_path + ')';
    // });
});