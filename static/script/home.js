window.onscroll = function () {
    checkscroll();
};
$(document).ready(function () {
    $("a").on("click", function (event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $("html, body").animate({
                    scrollTop: $(hash).offset().top - 72,
                },
                800,
                function () {
                    window.location.hash = hash - 72;
                }
            );
        }
    });
});



// All Application's functions starts here
const checkscroll=()=>{
    if(window.scrollY>100){
        document.getElementById("site-header").style.backgroundColor = "#000000";
    }else{
        if (document.querySelector(".nav_wrapper").classList.contains("active")){
            document.getElementById("site-header").style.backgroundColor = "#000000";
        }else{
                    document.getElementById("site-header").style.backgroundColor = "transparent";
        }
    }
    if (window.scrollY > 100) {
        document.getElementById("moveUp").style.animationDuration = "0.5s";
        document.getElementById("moveUp").style.display = "block";
        document.getElementById("themeBody").style.animationName = "slideUp";
        document.getElementById("moveUp").style.animationName = "slideIn";
    } else {
        document.getElementById("moveUp").style.animationDuration = "0.25s";
        document.getElementById("themeBody").style.animationName = "slideDown";
        document.getElementById("moveUp").style.animationName = "slideOut";
    }
}

function checkTheme(){
    if (window.localStorage.getItem("theme") == "dark") {
        changeTheme(0);
    } else if (window.localStorage.getItem("theme") == "light") {
        changeTheme(1);
    } else {
        window.localStorage.setItem("theme", "dark");
    }
}

// function checkLoginStatus(checkIflogin) {
//     if (checkIflogin == "true") {
//         document.getElementById("login").style.display = "none";
//         document.getElementById("signup").style.display = "none";
//         document.getElementById("logout").style.display = "block";
//     } else {
//         document.getElementById("login").style.display = "block";
//         document.getElementById("signup").style.display = "block";
//         document.getElementById("logout").style.display = "none";
//     }
// }