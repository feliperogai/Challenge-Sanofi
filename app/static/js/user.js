document.addEventListener('DOMContentLoaded', function () {
    let currentPage = 0; // Página inicial
    const ticketsPerPage = 3; // Ajustado para 3 tickets por página

    // Indicador de carregamento
    const loadingIndicator = document.getElementById('loadingIndicator'); // Certifique-se de que este elemento existe no HTML
    loadingIndicator.style.display = 'none'; // Ocultar inicialmente

    // Carregar tickets do usuário
    function loadUserTickets() {
        loadingIndicator.style.display = 'block'; // Mostrar indicador de carregamento
        fetch(`/api/tickets/user?page=${currentPage}&limit=${ticketsPerPage}`, {
            method: 'GET',
            credentials: 'include' // Para incluir cookies na requisição
        })
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar tickets.');
            return response.json();
        })
        .then(tickets => {
            const ticketsList = document.getElementById('tickets-container');
            ticketsList.innerHTML = '';

            if (tickets.length === 0) {
                ticketsList.innerHTML = '<p>Nenhum ticket encontrado.</p>';
            }

            tickets.forEach(ticket => {
                const ticketDiv = document.createElement('div');
                ticketDiv.classList.add('ticket');
                ticketDiv.innerHTML =
                    `<h3>${ticket.nome_treinamento}</h3>
                     <p>Data: ${formatDate(ticket.data_hora)}</p>
                     <p>Link: <a href="${ticket.link}" target="_blank">Acessar</a></p>
                     <a href="#" onclick="showTicketDetails(${ticket.id})">Ver Detalhes</a>`;
                ticketsList.appendChild(ticketDiv);
            });

            // Habilitar ou desabilitar botões de navegação
            document.getElementById('prev-tickets').style.display = currentPage > 0 ? 'inline-block' : 'none';
            document.getElementById('next-tickets').style.display = tickets.length < ticketsPerPage ? 'none' : 'inline-block';
        })
        .catch(error => {
            console.error('Erro ao carregar tickets:', error);
            alert(error.message);  // Exibir erro ao usuário
        })
        .finally(() => {
            loadingIndicator.style.display = 'none'; // Ocultar indicador de carregamento
        });
    }

    // Função para mostrar detalhes do ticket
    window.showTicketDetails = function (ticketId) {
        fetch(`/api/tickets/${ticketId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ticket não encontrado');
                }
                return response.json();
            })
            .then(ticket => {
                document.getElementById('modal-titulo').textContent = ticket.nome_treinamento;

                // Atualize o campo de usuários
                document.getElementById('modal-usuarios').textContent = '';

                // Exibir o status do treinamento
                const statusElement = document.getElementById('modal-treinamento');
                const treinamentoStatus = ticket.concluido ? 'Presente' : 'Ausente';
                statusElement.textContent = treinamentoStatus;

                // Adicionar a classe correspondente
                if (ticket.concluido) {
                    statusElement.classList.add('presente');
                    statusElement.classList.remove('ausente');
                } else {
                    statusElement.classList.add('ausente');
                    statusElement.classList.remove('presente');
                }

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
    document.querySelector('.close').addEventListener('click', function () {
        document.getElementById('ticket-modal').style.display = 'none';
    });

    // Funções de paginação de tickets
    document.getElementById('prev-tickets').addEventListener('click', function () {
        if (currentPage > 0) {
            currentPage--;
            loadUserTickets();
        }
    });

    document.getElementById('next-tickets').addEventListener('click', function () {
        currentPage++;
        loadUserTickets();
    });

    // Carregar gráfico do usuário
    function loadUserChart() {
        fetch('/api/progress/user', {
            method: 'GET',
            credentials: 'include' // Para incluir cookies na requisição
        })
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar os dados do gráfico.');
            return response.json();
        })
        .then(data => {
            const labels = ['Não Concluídos', 'Concluídos'];
            const concluded = data.treinamentos_concluidos || 0;
            const notConcluded = data.treinamentos_nao_concluidos || 0;

            const ctx = document.getElementById('grafico-desempenho').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Treinamentos Concluídos',
                            data: [concluded],
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Treinamentos Não Concluídos',
                            data: [notConcluded],
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
            alert(error.message);  // Exibir erro ao usuário
        });
    }

    // Formatar data para dd-mm-yyyy
    function formatDate(dateString) {
        // Exemplo de formatação 'DD-MM-YYYY'
        const parts = dateString.split('-'); // Ajuste conforme o formato
        if (parts.length !== 3) {
            return 'Data inválida';
        }
        const day = parts[0];
        const month = parts[1];
        const year = parts[2];
    
        const formattedDate = new Date(`${year}-${month}-${day}`);
        
        // Verifica se a data é válida
        if (isNaN(formattedDate.getTime())) {
            return 'Data inválida';
        }
    
        return `${day}-${month}-${year}`;
    }

    // Carregar os dados ao iniciar
    loadUserTickets();
    loadUserChart();
});
