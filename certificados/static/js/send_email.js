document.addEventListener('DOMContentLoaded', function () {
    const check_send_email = document.getElementById('send_email')

    email_table = document.getElementById('email_table')

    check_send_email.addEventListener('change', function (event) {
        if (check_send_email.checked) {
            email_table.style.display = 'table'
        } else {
            email_table.style.display = 'none'
        }
    })

    const form = document.getElementById('form')

    form.addEventListener('submit', function (event) {
        if (check_send_email.checked) {
            pdf_input = document.getElementById('id_pdf_certificate')
            email_input = document.getElementById('id_email')
            if (pdf_input.files.length === 0 || email_input.value.trim() === '') {
                event.preventDefault()
                alert('Por favor, selecione um arquivo válido e preencha o email do aluno.')
                loadingSpinner = document.getElementById('loading-spinner')
                loadingSpinner.style.display = 'none'
            }
        }
    })
})