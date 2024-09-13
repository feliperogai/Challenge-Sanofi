document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Evita o envio do formulário

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) { // Verifica se a resposta HTTP foi bem-sucedida
            if (data.redirect) {
                console.log(`Redirecionando para: ${data.redirect}`);  // Log para depuração
                window.location.href = data.redirect;  // Redireciona para a página do usuário/admin
            } else {
                alert(data.mensagem || 'Erro desconhecido.');
            }
        } else {
            alert(data.mensagem || 'Erro desconhecido.');
        }
    } catch (error) {
        console.error('Erro:', error);  // Log para depuração
        alert('Erro na comunicação com o servidor.');
    }
});
