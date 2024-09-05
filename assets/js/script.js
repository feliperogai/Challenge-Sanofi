document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Evita o envio do formulário

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();

        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            alert(data.mensagem || 'Erro desconhecido.');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro na comunicação com o servidor.');
    }
});
