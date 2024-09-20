// Função para exibir o menu lateral
function toggleMenu() {
    const sideMenu = document.getElementById('side-menu');
    sideMenu.style.width = sideMenu.style.width === '250px' ? '0' : '250px';
}

// Função para fechar o menu lateral
function closeMenu() {
    document.getElementById('side-menu').style.width = '0';
}

// Função para exibir uma mensagem de feedback
function displayFeedback(message, type) {
    const feedbackElement = document.getElementById('feedbackMessage');
    feedbackElement.textContent = message;
    feedbackElement.className = `feedback ${type}`;
    feedbackElement.style.display = 'block';
}

// Função para carregar e exibir usuários
function loadUsers() {
    fetch('/api/users')
        .then(response => response.json())
        .then(users => {
            const tableBody = document.getElementById('usersTable').getElementsByTagName('tbody')[0];
            tableBody.innerHTML = ''; // Limpa o corpo da tabela antes de adicionar novos dados
            
            users.forEach(user => {
                const row = tableBody.insertRow();
                row.insertCell(0).textContent = user.id;
                row.insertCell(1).textContent = user.nome;
                row.insertCell(2).textContent = user.email;
                row.insertCell(3).textContent = user.tipo;

                const actionsCell = row.insertCell(4);
                actionsCell.innerHTML = `
                    <button class="button button-warning" onclick="changeUserType(${user.id})">Alterar Tipo</button>
                    <button class="button button-danger" onclick="deleteUser(${user.id})">Excluir</button>
                `;
            });
        })
        .catch(error => {
            console.error('Erro ao carregar usuários:', error);
            displayFeedback('Erro ao carregar usuários.', 'error');
        });
}

// Função para alterar o tipo de usuário
function changeUserType(userId) {
    const newType = prompt('Digite o novo tipo de usuário (admin/user):');
    if (!newType) return;

    fetch('/api/user-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'change-user-type': 'true',
            'user-id': userId,
            'new-type': newType
        })
    })
    .then(response => response.json())
    .then(data => {
        displayFeedback(data.message, data.status);
        if (data.status === 'success') {
            loadUsers(); // Recarrega a lista de usuários
        }
    })
    .catch(error => {
        console.error('Erro ao alterar o tipo de usuário:', error);
        displayFeedback('Erro ao alterar o tipo de usuário.', 'error');
    });
}

// Função para excluir um usuário
function deleteUser(userId) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) return;

    fetch('/api/user-settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'delete-user': 'true',
            'user-id': userId
        })
    })
    .then(response => response.json())
    .then(data => {
        displayFeedback(data.message, data.status);
        if (data.status === 'success') {
            loadUsers(); // Recarrega a lista de usuários
        }
    })
    .catch(error => {
        console.error('Erro ao excluir o usuário:', error);
        displayFeedback('Erro ao excluir o usuário.', 'error');
    });
}

// Inicializa a página
document.addEventListener('DOMContentLoaded', function() {
    loadUsers(); // Carrega a lista de usuários ao iniciar
});
