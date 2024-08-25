document.addEventListener('DOMContentLoaded', () => {
    const emailFiltrado = document.getElementById('email-filtrado');
    const ticketsContainer = document.getElementById('tickets-container');
    const ctx = document.getElementById('grafico-desempenho').getContext('2d');
    const prevButton = document.getElementById('prev-tickets');
    const nextButton = document.getElementById('next-tickets');

    const emailUsuario = "user@sanofi.com.br"; // E-mail fixo do usuário
    let treinamentos = JSON.parse(localStorage.getItem('treinamentos')) || [];
    const ticketsPorPagina = 4;
    let paginaAtual = 0;

    function updateEmailFiltrado() {
        emailFiltrado.textContent = `E-mail: ${emailUsuario}`;
    }

    function updateTickets() {
        const treinamentosUsuario = treinamentos.filter(t => t.usuario === emailUsuario);
        const start = paginaAtual * ticketsPorPagina;
        const end = start + ticketsPorPagina;
        const treinamentosPagina = treinamentosUsuario.slice(start, end);

        ticketsContainer.innerHTML = '';

        treinamentosPagina.forEach(treinamento => {
            const ticket = document.createElement('div');
            ticket.className = 'ticket';

            ticket.innerHTML = `
                <h3>${treinamento.treinamento}</h3>
                <p>Data: ${treinamento.data}</p>
                <p>Status: <span class="${treinamento.concluido ? 'concluido' : 'nao-concluido'}">${treinamento.concluido ? 'Concluído' : 'Não Concluído'}</span></p>
                ${treinamento.arquivo ? `<a href="${treinamento.arquivo}" target="_blank">Ver Arquivo</a>` : '<p>Nenhum Arquivo</p>'}
            `;

            ticketsContainer.appendChild(ticket);
        });

        prevButton.disabled = paginaAtual === 0;
        nextButton.disabled = end >= treinamentosUsuario.length;
    }

    function updateGrafico() {
        const treinamentosUsuario = treinamentos.filter(t => t.usuario === emailUsuario);
        const dadosConcluidos = treinamentosUsuario.filter(t => t.concluido).length;
        const dadosNaoConcluidos = treinamentosUsuario.length - dadosConcluidos;

        if (window.myChart) {
            window.myChart.destroy();
        }

        if (treinamentosUsuario.length > 0) {
            window.myChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Concluído', 'Não Concluído'],
                    datasets: [{
                        data: [dadosConcluidos, dadosNaoConcluidos],
                        backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)'],
                        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    },
                    maintainAspectRatio: false
                }
            });
        } else {
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            ctx.font = "20px Arial";
            ctx.textAlign = "center";
            ctx.fillText("Nenhum dado disponível", ctx.canvas.width / 2, ctx.canvas.height / 2);
        }
    }

    prevButton.addEventListener('click', () => {
        if (paginaAtual > 0) {
            paginaAtual--;
            updateTickets();
        }
    });

    nextButton.addEventListener('click', () => {
        if ((paginaAtual + 1) * ticketsPorPagina < treinamentos.filter(t => t.usuario === emailUsuario).length) {
            paginaAtual++;
            updateTickets();
        }
    });

    // Inicializa a página com os dados existentes para o usuário fixo
    updateEmailFiltrado();
    updateTickets();
    updateGrafico();
});
