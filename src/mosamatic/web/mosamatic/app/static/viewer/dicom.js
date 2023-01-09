const element = document.getElementById("container");
cornerstone.enabled(element);

const imageId = "example://1";
cornerstone.loadImage(imageId).then(function(image) {
    cornerstone.displayImage(element, image);
});