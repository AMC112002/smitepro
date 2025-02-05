// static/js/loader.js
window.addEventListener("pageshow", function(event) {
    const loader = document.getElementById("loader");
    if (event.persisted) {
        // Si la página fue cargada desde el caché, ocultamos el loader
        if (loader) {
            loader.classList.remove("d-flex"); // Quita la clase 'd-flex'
            loader.style.display = "none";
        }
    } else {
        // Si es una carga normal, también ocultamos el loader
        if (loader) {
            loader.classList.remove("d-flex"); // Quita la clase 'd-flex'
            loader.style.display = "none";
        }
    }
});

window.addEventListener("beforeunload", function() {
    const loader = document.getElementById("loader");
    if (loader) {
        loader.classList.add("d-flex"); // Agrega la clase 'd-flex' de nuevo
        loader.style.display = "flex"; // Muestra el loader
    }
});
