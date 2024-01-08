function submitForm() {
    var summonername = document.getElementById("summonername").value;
    var tagline = document.getElementById("tagline").value;

    var formData = {
        summonername: summonername,
        tagline: tagline
    };

    fetch('http://localhost:5000/get_recent_games', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response=>response.json())
    .then(data=> {
        displayResults(data)
    })
    .catch(error=>console.error("Error:", error));
}

function displayResults(data) {
    // Update the result div with the fetched data
    var resultDiv = document.getElementById("result");
    resultDiv.innerHTML = JSON.stringify(data, null, 2);
}