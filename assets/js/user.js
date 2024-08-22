document.addEventListener('DOMContentLoaded', () => {
    const tabelaTreinamentos = document.getElementById('tabela-treinamentos').getElementsByTagName('tbody')[0];
    const usuarioNome = document.getElementById('usuario-nome'); // Elemento para exibir o nome do usuário
    const noTreinamentos = document.getElementById('no-treinamentos'); // Elemento para exibir mensagem se não houver dados

    // Obtemos o nome do usuário a partir do localStorage
    const nomeUsuario = localStorage.getItem('nomeUsuario') || 'Usuário Desconhecido';
    
    // Atualiza o nome do usuário na página
    usuarioNome.textContent = nomeUsuario;

    let treinamentos = JSON.parse(localStorage.getItem('treinamentos')) || [];

    function updateTabelaTreinamentos() {
        // Filtra os treinamentos para o usuário atual
        const treinamentosUsuario = treinamentos.filter(t => t.usuario === nomeUsuario);

        if (treinamentosUsuario.length === 0) {
            noTreinamentos.textContent = 'Nenhum treinamento encontrado.';
        } else {
            noTreinamentos.textContent = '';
        }

        tabelaTreinamentos.innerHTML = '';

        treinamentosUsuario.forEach(treinamento => {
            const row = tabelaTreinamentos.insertRow();
            const cellTreinamento = row.insertCell();
            const cellData = row.insertCell();
            const cellArquivo = row.insertCell();
            const cellConcluido = row.insertCell();

            cellTreinamento.textContent = treinamento.treinamento;
            cellData.textContent = treinamento.data;
            cellArquivo.innerHTML = treinamento.arquivo ? `<a href="${treinamento.arquivo}" target="_blank">Ver Arquivo</a>` : 'Nenhum Arquivo';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = treinamento.concluido;
            checkbox.disabled = true; // Desabilitar o checkbox, pois o usuário não deve modificar
            cellConcluido.appendChild(checkbox);
        });
    }

    // Inicializa a página com os dados existentes
    updateTabelaTreinamentos();
});
