document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form')
    const loadingSpinner = document.getElementById('loading-spinner')

    form.addEventListener('submit', function (event) {
        loadingSpinner.classList.remove('d-none')
    })
})