
const canvas = document.getElementById("background");
const ctx = canvas.getContext("2d");

const Background = {
    maxParticles: 200,
    particleWidth: 14,
    particleHeight: 14,
    particles: [],

    mode: "matrix",

    colorIndex: 0,
    matrixColor: "rgb(63, 243, 147)",
    prideColors: ["#E40303", "#F04400", "#FF8C00", "#FFB400", "#FFED00", "#8FCB00", "#008026", "#006B83", "#004DFF", "#3A2FB5", "#750787"],
    allowedChars: "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンあいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん",

    t: 0,
    deltaMove: (t, p) => [0, 1],

    interval: 1000 / 12,

    initParticles: function() {
        console.log("Initializing particles: ", Background.maxParticles);

        for (let i = 0; i < canvas.width / Background.particleWidth; i++) {
            this.particles.push([
                Background.particleWidth * i,
                Math.floor(Math.random() * canvas.height)
            ]);
        }
    },

    render: function(ctx) {
        console.log("asd");

        ctx.fillStyle = "rgba(3, 7, 17, 0.2)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        switch (Background.mode) {
            case "matrix":
                ctx.fillStyle = Background.matrixColor;
                break;

            case "pride":
                ctx.fillStyle = Background.prideColors[
                    Math.floor(Background.colorIndex) % Background.prideColors.length];
                Background.colorIndex += 1 / 3;
                break;
        }  

        Background.particles.forEach((p) => {
            d = Background.deltaMove(Background.t, p);

            p[0] += Background.particleWidth * d[0];
            p[1] += Background.particleHeight * d[1];

            console.log(p);

            // Move out-of-sight partibles back to the screen
            if (p[1] < 0) p[1] += canvas.height;
            if (p[1] > canvas.height) p[1] -= canvas.height;
            // if (p[0] < 0) p[0] -= canvas.width;
            // if (p[0] > canvas.width) p[0] -= canvas.width;

            // Draw particle
            ctx.fillText(
                Background.allowedChars[Math.floor(Math.random() * Background.allowedChars.length)],
                p[0], p[1]
            );
        });

        Background.t += 1;
    }
}

window.onload = function() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    Background.initParticles();

    Background.deltaMove = (t, p) => [
        - 0.2 * Math.cos(Math.PI * p[0] / canvas.width) * Math.cos(Math.PI * p[1] / canvas.height),
        1
    ];

    setInterval(
        Background.render,
        Background.interval,
        ctx
    );
}