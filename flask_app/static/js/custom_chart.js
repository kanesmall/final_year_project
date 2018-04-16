$.getJSON('https://ksmall.me/show_trends/1', function(json) {
	
	let labels = [];
	let data = [];
	for (i = 0; i < json.length; i++) {
		labels.push(json[i]['trend1']);
		data.push((json[i]['trend2'] / 1000000000).toFixed(2));
	}
	
    // Bar chart
    new Chart(document.getElementById("trend1_barchart"), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: "Revenue (billions)",
              backgroundColor: ['rgba(26, 188, 156, 0.4)', 'rgba(46, 204, 113, 0.4)', 'rgba(52, 152, 219, 0.4)', 'rgba(155, 89, 182, 0.4)', 'rgba(52, 73, 94, 0.4)', 'rgba(22, 160, 133, 0.4)', 'rgba(39, 174, 96, 0.4)', 'rgba(41, 128, 185, 0.4)', 'rgba(142, 68, 173, 0.4)', 'rgba(44, 62, 80, 0.4)', 'rgba(241, 196, 15, 0.4)', 'rgba(230, 126, 34, 0.4)', 'rgba(231, 76, 60, 0.4)', 'rgba(236, 240, 241, 0.4)', 'rgba(149, 165, 166, 0.4)', 'rgba(243, 156, 18, 0.4)', 'rgba(211, 84, 0, 0.4)', 'rgba(192, 57, 43, 0.4)', 'rgba(189, 195, 199, 0.4)', 'rgba(127, 140, 141, 0.4)'],
			  borderColor: ['rgba(26, 188, 156, 1)', 'rgba(46, 204, 113, 1)', 'rgba(52, 152, 219, 1)', 'rgba(155, 89, 182, 1)', 'rgba(52, 73, 94, 1)', 'rgba(22, 160, 133, 1)', 'rgba(39, 174, 96, 1)', 'rgba(41, 128, 185, 1)', 'rgba(142, 68, 173, 1)', 'rgba(44, 62, 80, 1)', 'rgba(241, 196, 15, 1)', 'rgba(230, 126, 34, 1)', 'rgba(231, 76, 60, 1)', 'rgba(236, 240, 241, 1)', 'rgba(149, 165, 166, 1)', 'rgba(243, 156, 18, 1)', 'rgba(211, 84, 0, 1)', 'rgba(192, 57, 43, 1)', 'rgba(189, 195, 199, 1)', 'rgba(127, 140, 141, 1)'],
			  borderWidth: 2,
              data: data
            }
          ]
        },
        options: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Highest grossing genre (billions)'
          },
		  responsive: true
        }
    });
    
});

$.getJSON('https://ksmall.me/show_trends/2', function(json) {
	
	let labels = [];
	let data = [];
	for (i = 0; i < json.length; i++) {
		labels.push(json[i]['trend1']);
		data.push((json[i]['trend2'] / 1000000000).toFixed(2));
	}
	
    // Bar chart
    new Chart(document.getElementById("trend2_barchart"), {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: "Revenue (billions)",
              backgroundColor: ['rgba(26, 188, 156, 0.4)', 'rgba(46, 204, 113, 0.4)', 'rgba(52, 152, 219, 0.4)', 'rgba(155, 89, 182, 0.4)', 'rgba(52, 73, 94, 0.4)', 'rgba(22, 160, 133, 0.4)', 'rgba(39, 174, 96, 0.4)', 'rgba(41, 128, 185, 0.4)', 'rgba(142, 68, 173, 0.4)', 'rgba(44, 62, 80, 0.4)'],
			  borderColor: ['rgba(26, 188, 156, 1)', 'rgba(46, 204, 113, 1)', 'rgba(52, 152, 219, 1)', 'rgba(155, 89, 182, 1)', 'rgba(52, 73, 94, 1)', 'rgba(22, 160, 133, 1)', 'rgba(39, 174, 96, 1)', 'rgba(41, 128, 185, 1)', 'rgba(142, 68, 173, 1)', 'rgba(44, 62, 80, 1)'],
			  borderWidth: 2,
              data: data
            }
          ]
        },
        options: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Highest grossing genre (billions)'
          },
		  responsive: true
        }
    });
    
});