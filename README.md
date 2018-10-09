# Slide Extractor
A python script designed to extract slides from lecture videos.

## Installation

Clone the git repository and install the required modules:

```shell
$ git clone https://github.com/realChesta/slide-extractor.git
$ cd slide-extractor
$ pip install -r requirements.txt
```

## Usage

### Downloading a video to extract the slides from

Here is a simple way to download the needed part of a lecture video:

- Navigate to the website where the player of your video is located.
- (in Google Chrome) *Right click* the player and select `Inspect`.

   Alternatively, you can also open the console directly and change the context from `top` to the player.

- Paste the following into the console:

   ```javascript
   window.data.streams.find(function(s){return!!(s.sources.mp4&&s.sources.mp4.length>0)&&s.sources.mp4[0].src.includes("presentation")}).sources.mp4.forEach(function(s){console.log(s.src)});
   ```
   *(see `video-finder.js`)*

- You will now see one or more links, click one and **download the video it leads to**.

### Running Slide Extractor

You can run Slide Extractor the following way:
```shell
$ cd slide-extractor
$ python main.py -v "yourpath/video.mp4"
```
*(replace `"yourpath/video.mp4"` with your video file.)*


### Options

* `-v, --video [path]` *(required)* sets the video file to use. 
* `-o, --output [path]` sets the filename of the pdf containing the extracted slides. Default is `"slides.pdf"`.
* `-s, --step-size [num]` sets how many frames should be skipped in each iteration. The higher the number, the faster, but could lead to missed slides. Default is `20`.
* `-p --progress-interval [num]` sets how often the program should report it's progress (in percent). Example: if set to `5`, the program will send a message every 5 percent it makes. Default is `1`.


