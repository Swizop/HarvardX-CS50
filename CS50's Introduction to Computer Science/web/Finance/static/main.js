function listen() {

console.log("abc");
let input = document.getElementById("symbolinp");
input.addEventListener('keyup', function() {
    $.get('/nasdaq?q=' + input.value, function(stocks) {
        let html = '';
        for (let s in stocks) {
            let symbol = stocks[s].symbol.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;');
            html += '<li class="list-group-item">' + symbol + '</li>';
        }
        document.getElementById("ul").innerHTML = html;
    });
});
}


document.addEventListener('DOMContentLoaded', listen);