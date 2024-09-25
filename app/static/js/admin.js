document.addEventListener('DOMContentLoaded', function () {
    let currentPage = 0; // Página inicial
    const ticketsPerPage = 4; // Ajustado para 4 tickets por página
    let selectedUsers = [];

    // Carregar usuários ao iniciar
    function loadUsers() {
        fetch('/api/users')
            .then(response => response.json())
            .then(users => {
                const usuarioList = document.getElementById('usuario-list');
                usuarioList.innerHTML = ''; // Limpar a lista anterior

                users.forEach(user => {
                    if (user.tipo === 'user') {
                        const label = document.createElement('label');
                        const checkbox = document.createElement('input');
                        checkbox.type = 'checkbox';
                        checkbox.value = user.id; // Valor é o ID do usuário

                        // Adicionar evento para atualizar a seleção
                        checkbox.addEventListener('change', () => {
                            if (checkbox.checked) {
                                selectedUsers.push(user);
                            } else {
                                selectedUsers = selectedUsers.filter(u => u.id !== user.id);
                            }
                            updateUserDisplay();
                        });

                        label.appendChild(checkbox);
                        label.appendChild(document.createTextNode(user.nome)); // Nome do usuário
                        usuarioList.appendChild(label);
                    }
                });
            })
            .catch(error => {
                console.error('Erro ao carregar usuários:', error);
            });
    }

    // Atualizar exibição de usuários selecionados
    function updateUserDisplay() {
        const usuarioInput = document.getElementById('usuario');
        usuarioInput.value = selectedUsers.length > 0 ? selectedUsers.map(u => u.nome).join(', ') : 'Selecione os usuários';
    }

    // Mostrar/ocultar a lista de usuários ao clicar
    window.toggleUserSelection = function() {
        const usuarioList = document.getElementById('usuario-list');
        usuarioList.style.display = usuarioList.style.display === 'none' ? 'block' : 'none';
    };

    // Fechar a lista se clicar fora
    document.addEventListener('click', function(event) {
        const usuarioContainer = document.getElementById('usuario-container');
        const usuarioList = document.getElementById('usuario-list');
        if (!usuarioContainer.contains(event.target)) {
            usuarioList.style.display = 'none';
        }
    });

    // Carregar tickets
    function loadTickets() {
        fetch(`/api/tickets?page=${currentPage}&limit=${ticketsPerPage}`) // Mantém a limitação a 4 tickets
            .then(response => response.json())
            .then(tickets => {
                const ticketsList = document.getElementById('tickets-container');
                ticketsList.innerHTML = '';

                tickets.forEach(ticket => {
                    const ticketDiv = document.createElement('div');
                    ticketDiv.classList.add('ticket');
                    ticketDiv.innerHTML = `
                        <h3>${ticket.nome_treinamento}</h3>
                        <p>Usuários: ${ticket.num_usuarios}</p>
                        <p>Data: ${formatDate(ticket.data)}</p>
                        <p>Horário: ${ticket.time}</p>
                        <a href="#" onclick="showTicketDetails(${ticket.id})">Ver Detalhes</a>
                    `;
                    ticketsList.appendChild(ticketDiv);
                });

                // Habilitar ou desabilitar botões de navegação
                document.getElementById('prev-tickets').style.display = currentPage > 0 ? 'inline-block' : 'none';
                document.getElementById('next-tickets').style.display = tickets.length < ticketsPerPage ? 'none' : 'inline-block';
            })
            .catch(error => {
                console.error('Erro ao carregar tickets:', error);
            });
    }

    // Formatar data para dd-mm-yyyy
    function formatDate(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Janeiro é 0
        const year = date.getFullYear();
        return `${day}-${month}-${year}`;
    }

    // Enviar o formulário de cadastro de treinamento
    document.getElementById('form-treinamento').addEventListener('submit', function (event) {
        event.preventDefault();

        const treinamento = document.getElementById('treinamento').value;
        const data = document.getElementById('data').value;
        const time = document.getElementById('time').value;
        const link = document.getElementById('link').value;

        fetch('/cadastrar-treinamento', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ usuario_ids: selectedUsers.map(u => u.id), treinamento, data, time, link }),
        })
        .then(response => {
            if (!response.ok) throw new Error('Erro ao cadastrar o treinamento');
            return response.json();
        })
        .then(data => {
            document.getElementById('confirmation-message').textContent = data.mensagem;
            document.getElementById('form-treinamento').reset();
            selectedUsers = []; // Limpar seleção
            updateUserDisplay(); // Atualiza exibição de usuários
            loadTickets(); // Atualiza a lista de tickets
        })
        .catch(error => {
            console.error('Erro:', error);
            document.getElementById('confirmation-message').textContent = 'Erro ao cadastrar o treinamento';
        });
    });

    // Função para mostrar detalhes do ticket
    window.showTicketDetails = function(ticketId) {
        fetch(`/api/tickets/${ticketId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ticket não encontrado');
                }
                return response.json();
            })
            .then(ticket => {
                document.getElementById('modal-titulo').textContent = ticket.nome_treinamento;
                document.getElementById('modal-usuarios').textContent = ticket.usuarios;
                document.getElementById('modal-data').textContent = formatDate(ticket.data);
                document.getElementById('modal-horario').textContent = ticket.time;
                const modalLink = document.getElementById('modal-link');
                modalLink.href = ticket.link;
                modalLink.textContent = 'Acessar treinamento';
                document.getElementById('ticket-modal').style.display = 'block';
            })
            .catch(error => {
                console.error('Erro ao carregar detalhes do ticket:', error);
                alert('Erro ao carregar os detalhes do ticket.');
            });
    };

    // Função para fechar o modal
    document.querySelector('.close').addEventListener('click', function() {
        document.getElementById('ticket-modal').style.display = 'none';
    });

    // Funções de paginação de tickets
    document.getElementById('prev-tickets').addEventListener('click', function() {
        if (currentPage > 0) {
            currentPage--;
            loadTickets();
        }
    });

    document.getElementById('next-tickets').addEventListener('click', function() {
        currentPage++;
        loadTickets();
    });

    // Carregar gráfico de desempenho
    function loadChart() {
        fetch('/api/progress')
            .then(response => {
                if (!response.ok) throw new Error('Erro ao carregar os dados do gráfico.');
                return response.json();
            })
            .then(data => {
                // Verifique se data é um array
                if (!Array.isArray(data)) {
                    throw new Error('Dados retornados não são um array.');
                }
    
                const labels = data.map(training => training.nome_usuario); // Ajustado para nome do usuário
                const concluded = data.map(training => training.treinamentos_concluidos);
                const notConcluded = data.map(training => training.treinamentos_nao_concluidos);
    
                const ctx = document.getElementById('progressChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Treinamentos Concluídos',
                                data: concluded,
                                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                borderColor: 'rgba(75, 192, 192, 1)',
                                borderWidth: 1
                            },
                            {
                                label: 'Treinamentos Não Concluídos',
                                data: notConcluded,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            })
            .catch(error => {
                console.error('Erro ao carregar o gráfico de desempenho:', error);
                document.getElementById('chart-error').textContent = 'Erro ao carregar os dados do gráfico.';
            });
    }    
    
    // Carregar gráfico ao iniciar
    loadChart();
    loadUsers();
    loadTickets();
});