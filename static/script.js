function initialize() {
    document.getElementById('query').addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            search();
        }
    });
}

function search() {
    var query = document.getElementById('query').value;

    fetch('/search?query=' + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => displayResults(data))
        .catch(error => console.error('Error:', error));
}

//function displayResults(results) {
//    var resultsContainer = document.getElementById('results');
//    resultsContainer.innerHTML = '';
//
//
//    if (results.length === 0) {
//        resultsContainer.innerText = 'Не найдено!';
//        return;
//    }
//    results.forEach(result => {
//        var resultDiv = document.createElement('div');
//        resultDiv.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
//        resultsContainer.appendChild(resultDiv);
//    });
//}

function displayResults(results) {
    var resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';

    if (results.length === 0) {
        resultsContainer.innerText = 'Не найдено!';
        return;
    }

    results.forEach((result, index) => {
        var resultDiv = document.createElement('div');
        resultDiv.innerHTML = '<pre>' + formatResult(result, index + 1) + '</pre>';
        resultsContainer.appendChild(resultDiv);
    });
}

function formatResult(result, index) {
    var formattedResult = '<strong id="result-text">Result ' + index + '</strong><br>';

    // Display 'title' first if available
    if (result.hasOwnProperty('title')) {
        formattedResult += '<strong>Имя:</strong> ' + result.title + '<br>';
    }

    // Display 'text' next if available
    if (result.hasOwnProperty('text')) {
        formattedResult += '<strong>Текст:</strong> ' + result.text + '<br>';
    }

    // Display 'categories' next if available
    if (result.hasOwnProperty('categories')) {
        formattedResult += '<strong>Категории:</strong> ' + result.categories.join(', ') + '<br>';
    }

    // Display remaining fields
    for (var key in result) {
        if (result.hasOwnProperty(key) && key !== 'title' && key !== 'text' && key !== 'categories') {
            var value = result[key];

            // Handle null values
            if (value === null) {
                formattedResult += '<strong>' + key + ':</strong> Нет данных<br>';
            } else {
                formattedResult += '<strong>' + key + ':</strong> ' + value + '<br>';
            }
        }
    }

    return formattedResult;
}

