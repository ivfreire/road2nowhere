
$("button#activate-message-writer").on("click", () => $("div#message-writer").toggle());



window.onmousemove = function(ev) {
    let dx = -(ev.clientX - window.innerWidth / 2) / 30;
    let dy = (ev.clientY - window.innerHeight / 2) / 15;
    let deg = Math.sqrt(dx*dx + dy*dy);

    $("div.header").css(
        "transform",
        `rotate3d(${dy}, ${dx}, 1, ${deg}deg)`
    );
}