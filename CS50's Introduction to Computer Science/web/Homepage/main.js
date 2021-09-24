let mail = document.getElementById("mail");
let mailExplain = document.getElementById("email-explained");
let job = document.getElementsByClassName("job")[0];
let il = document.getElementsByClassName("icon-list");
let explained = document.getElementsByClassName("explained");

let TextToCopy = "matei.neagu19@yahoo.com";

mail.addEventListener("click", () => {
    var TempText = document.createElement("input");
    TempText.value = TextToCopy;
    document.body.appendChild(TempText);
    TempText.select();
    
    document.execCommand("copy");
    document.body.removeChild(TempText);
    mailExplain.innerHTML = "Copied!";
});

il[0].addEventListener("mouseover", () => {
        explained[0].style.visibility = "visible";
    });
    il[1].addEventListener("mouseover", () => {
        explained[1].style.visibility = "visible";
    });
    il[2].addEventListener("mouseover", () => {
        explained[2].style.visibility = "visible";
    });

    il[0].addEventListener("mouseout", () => {
        explained[0].style.visibility = "hidden";
    });
    il[1].addEventListener("mouseout", () => {
        explained[1].style.visibility = "hidden";
    });
    il[2].addEventListener("mouseout", () => {
        explained[2].style.visibility = "hidden";
        mailExplain.innerHTML = "Copy email address";
    });