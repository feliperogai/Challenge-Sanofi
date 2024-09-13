async function logout() {
    try {
        // Envia uma solicitação POST para o servidor para realizar o logout
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();

        if (data.success) {
            // Redireciona o usuário para a página inicial após o logout
            window.location.href = data.redirect || '/';
        } else {
            alert(data.message || 'Erro desconhecido ao tentar sair.');
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro na comunicação com o servidor.');
    }
}

// Certifique-se de que o script está carregado no HTML
document.addEventListener('DOMContentLoaded', function() {
    const logoutButton = document.querySelector('a[onclick="logout()"]');
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }
});
