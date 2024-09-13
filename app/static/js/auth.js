async function checkAuth() {
    const token = getCookie('authToken');  // Buscar do cookie
    
    if (!token) {
        window.location.href = '/';  // Redireciona para a página de login se não estiver autenticado
        return;
    }

    try {
        const response = await fetch('/check-auth', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 401) {
            // Se o token for inválido, remove o cookie e redireciona para a página de login
            document.cookie = 'authToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Erro:', error);
        window.location.href = '/';  // Redireciona para a página de login em caso de erro
    }
}
