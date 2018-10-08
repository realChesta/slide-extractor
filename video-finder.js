//normal
JSON.parse(window.document.documentElement.innerHTML
    .match(/(data = )({[^]+})(;)/)[2])
    .streams.find(function (s) {
        if (s.sources.mp4 && s.sources.mp4.length > 0) {
            return s.sources.mp4[0].src.includes('presentation');
        }
        else { return false; }
    }).sources.mp4.forEach(function (mp4) {
        console.log(mp4.src);
    });

//minified
JSON.parse(window.document.documentElement.innerHTML.match(/(data = )({[^]+})(;)/)[2]).streams.find(function(e){return!!(e.sources.mp4&&e.sources.mp4.length>0)&&e.sources.mp4[0].src.includes("presentation")}).sources.mp4.forEach(function(e){console.log(e.src)});