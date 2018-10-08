//normal
window.data.streams.find(function (s) {
    if (s.sources.mp4 && s.sources.mp4.length > 0) {
        return s.sources.mp4[0].src.includes('presentation');
    }
    else { return false; }
}).sources.mp4.forEach(function (mp4) {
    console.log(mp4.src);
});

//minified
window.data.streams.find(function(s){return!!(s.sources.mp4&&s.sources.mp4.length>0)&&s.sources.mp4[0].src.includes("presentation")}).sources.mp4.forEach(function(s){console.log(s.src)});