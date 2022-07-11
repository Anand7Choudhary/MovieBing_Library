const getVideo = (n) => {
    document.getElementById("youtube-iframe").src = "https://www.youtube.com/embed/"+n + "?autoplay=1";
}