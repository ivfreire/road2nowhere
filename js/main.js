
const SERVER = "https://road2nowhere-api-219791393556.southamerica-east1.run.app"; // "http://localhost:3001";

/* ============================ Utilities ============================ */

function safeUrl(value) {
    try {
        const url = new URL(value);

        if (url.protocol !== "http:" && url.protocol !== "https:") {
            return null;
        }

        return url.href;
    } catch {
        return null;
    }
}


/* ============================ Image Zoom ============================ */

$('div.image-gallery img').each(function (index) {
    if ($(this).attr('onclick') != null) {                    
        if ($(this).attr('onclick').indexOf("runThis()") == -1) {                        
            $(this).click(function () {
                $(this).attr('onclick');
                var src = $(this).attr("src");
                ShowLargeImage(src);
            });
        }
    }
    else {                    
        $(this).click(function () {                        
            var src = $(this).attr("src");
            ShowLargeImage(src);
        });
    }
});

$('body').on('click', '.modal-overlay', function () {
    $('.modal-overlay, .modal-img').remove();
});

function ShowLargeImage(imagePath) {
    $('body').append('<div class="modal-overlay"><div class="modal-img"><img src="' + imagePath.replace("small","large") + '" /></div></div>');
}

/* ============================================================================= */

$("div#message-writer").draggable();

$("div.messages").ready(function() {
    console.log('Loading messages...');

    let payload = {source_page: window.location.pathname}

    $.ajax({
        url: SERVER + "/messages",
        type: "GET",
        data: payload,
        dataType: "json",
        success: function(res) {
            if (res.status !== "success") {
                console.log("Failed to load messages!");
                return;
            }

            res.messages.forEach((m) => {
                const x = Number(m.position_x) * window.innerWidth;
                const y = Number(m.position_y) * window.innerHeight;

                const $message = $("<div>")
                    .addClass("message window")
                    .css({
                        left: `${x}px`,
                        top: `${y}px`
                    });

                const $title = $("<div>")
                    .addClass("title")
                    .append(
                        $("<b>").text("message"),
                        $("<i>")
                            .addClass("fa-solid fa-xmark")
                            .attr("id", "close")
                    );

                const $content = $("<div>").addClass("content");

                $("<p>")
                    .append(
                        $("<b>").text("username: "),
                        document.createTextNode(m.username)
                    )
                    .appendTo($content);

                const url = safeUrl(m.url);

                const $urlRow = $("<p>")
                    .append($("<b>").text("website: "));

                if (url) {
                    $("<a>")
                        .attr("href", url)
                        .attr("rel", "noopener noreferrer nofollow ugc")
                        .text(m.url)
                        .appendTo($urlRow);
                } else {
                    $urlRow.append(document.createTextNode(m.url));
                }

                if (m.url) $urlRow.appendTo($content);

                $("<div>")
                    .addClass("body")
                    .append($("<p>").text(m.message))
                    .appendTo($content);

                $("<span>")
                    .text(m.timestamp)
                    .appendTo($content);

                $message.append($title, $content);

                $("div.messages").append($message);

                $message.draggable();
            });
        }
    });
});

$("div.message input#send").on('click', function() {
    let p = $(this).parent();

    let username = p.find("#username").val().trim();
    let url = p.find("#url").val().trim();
    let message = p.find("#message").val().trim();

    username = username || "anonymous";
    url = url || null;

    if (!message) {
        p.find("#status").html("Message body cannot be empty.");
        return;
    }

    if (username.length > 50 || message.length > 300) {
        p.find("#status").html("Username or message exceeds character count limit.");
        return;
    }

    if (url) {
        try {
            const parsed = new URL(url);
            if (!["http:", "https:"].includes(parsed.protocol)) {
                p.find("#status").html("Invalid URL. Only https:// and http:// protocols are allowed.");
                return;
            }
        } catch {
            p.find("#status").html("Invalid URL. Must include https:// or http://");
            return;
        }
    }

    let payload = {
        username: username,
        url: url,
        message: message,
        source_page: window.location.pathname,
        position_x: p.parent().offset().left / window.innerWidth,
        position_y: p.parent().offset().top / window.innerHeight
    }

    $.ajax({
        url: SERVER + "/messages",
        type: "POST",
        data: JSON.stringify(payload),
        contentType: "application/json",
        success: function(res) {
            if (res["status"] == "success") {
                p.find("#message").val("");
                p.find("#status").html("Message sent successfully!");
            } else {
                p.find("#status").html(res["message"]);
            }
        },
        dataType: "JSON"
    });
});

window.onclick = function(ev) {
    let target = ev.target;

    if (target.getAttribute("id") == "close") {
        let window = $(target.parentElement.parentElement);
        window.fadeOut();
    }
}

/* ============================================================================= */
