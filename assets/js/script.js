function validateLogin(event) {
    event.preventDefault(); // Evita o envio do formulário

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Verifica se o email e a senha correspondem ao admin
    if (email === 'admin' && password === 'admin') {
        // Redireciona para a página de controle se as credenciais forem corretas
        window.location.href = './assets/pages/admin.html';
    } 
    // Verifica se o email e a senha correspondem ao usuário comum
    else if (email === 'user' && password === 'user') {
        // Redireciona para a página de usuário se as credenciais forem corretas
        window.location.href = './assets/pages/user.html';
    } 
    else {
        // Exibe uma mensagem de erro se as credenciais estiverem incorretas
        alert('Email ou senha incorretos.');
    }
}         