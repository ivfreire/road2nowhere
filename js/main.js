import { GLOBAL } from "./config.js";
import { Message } from "./message.js";


window.onload = () => {
    GLOBAL.loadLocal();

    // After configs are loaded.
    Message.init(GLOBAL);
}


// Window events
window.onclick = function(ev) {
    let target = ev.target;

    if (target.getAttribute("id") == "close") {
        let window = $(target.parentElement.parentElement.parentElement);
        window.fadeOut();
    }

    if (target.getAttribute("id") == "toggle") {
        let window = $(target.parentElement.parentElement.parentElement).find(".content");
        window.slideToggle();
    }
}