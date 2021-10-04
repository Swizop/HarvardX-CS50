let edit = document.getElementsByClassName("edit");


function f1(id)
{
    id = id.slice(1, );
    var h2 = document.getElementById("h2");
    var form = document.getElementById("submit-form");
    var nameInput = document.getElementById("name-input");
    var dayInput = document.getElementById("day-input");
    var monthInput = document.getElementById("month-input");
    var birthday = document.getElementById("B" + id).innerHTML;

    nameInput.value = document.getElementById("N" + id).innerHTML;
    dayInput.value = birthday.slice(0, birthday.indexOf("/"));
    monthInput.value = birthday.slice(birthday.indexOf("/") + 1);

    h2.innerHTML = "Edit selected birthday";
    form.action = "/edit";
    var hidden = document.createElement("input");
    hidden.name = "id";
    hidden.type = "hidden";
    hidden.value = id;
    form.appendChild(hidden);

}


for(var i = 0; i < edit.length; i++)
{
    edit[i].addEventListener("click", function() {
        f1(this.id)} );
}