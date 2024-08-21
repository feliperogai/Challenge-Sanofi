document.addEventListener('DOMContentLoaded', () => {
    const formCadastro = document.getElementById('form-cadastro');
    const formNovoTreinamento = document.getElementById('form-novo-treinamento');
    const formTreinamento = document.getElementById('form-treinamento');
    const listaUsuarios = document.getElementById('lista-usuarios');
    const tabelaTreinamentos = document.getElementById('tabela-treinamentos').getElementsByTagName('tbody')[0];
    const usuarioSelect = document.getElementById('usuario');
    const treinamentoSelect = document.getElementById('treinamento');
    const ctx = document.getElementById('grafico-desempenho').getContext('2d');

    let usuarios = JSON.parse(localStorage.getItem('usuarios')) || [];
    let treinamentos = JSON.parse(localStorage.getItem('treinamentos')) || [];
    let tiposTreinamento = JSON.parse(localStorage.getItem('tiposTreinamento')) || [];

    const usuariosPorPagina = 2;
    const treinamentosPorPagina = 2;
    const tabelaPorPagina = 5;
    let paginaUsuarios = 0;
    let paginaTreinamentos = 0;
    let paginaTabela = 0;

    function saveData() {
        localStorage.setItem('usuarios', JSON.stringify(usuarios));
        localStorage.setItem('treinamentos', JSON.stringify(treinamentos));
        localStorage.setItem('tiposTreinamento', JSON.stringify(tiposTreinamento));
    }

    function updateUsuarioSelect() {
        usuarioSelect.innerHTML = '';
        usuarios.forEach(usuario => {
            const option = document.createElement('option');
            option.value = usuario;
            option.textContent = usuario;
            usuarioSelect.appendChild(option);
        });
    }

    function updateTreinamentoSelect() {
        treinamentoSelect.innerHTML = '';
        tiposTreinamento.forEach(treinamento => {
            const option = document.createElement('option');
            option.value = treinamento;
            option.textContent = treinamento;
            treinamentoSelect.appendChild(option);
        });
    }

    function updateUsuarioList() {
        const start = paginaUsuarios * usuariosPorPagina;
        const end = start + usuariosPorPagina;
        const usuariosPagina = usuarios.slice(start, end);

        listaUsuarios.innerHTML = '';
        usuariosPagina.forEach(usuario => {
            const li = document.createElement('li');
            li.textContent = usuario;
            listaUsuarios.appendChild(li);
        });

        document.getElementById('prev-usuarios').disabled = paginaUsuarios === 0;
        document.getElementById('next-usuarios').disabled = end >= usuarios.length;
    }

    function updateTabelaTreinamentos() {
        const start = paginaTabela * tabelaPorPagina;
        const end = start + tabelaPorPagina;
        const treinamentosPagina = treinamentos.slice(start, end);

        tabelaTreinamentos.innerHTML = '';

        treinamentosPagina.forEach((treinamento) => {
            const row = tabelaTreinamentos.insertRow();
            const cellUsuario = row.insertCell();
            const cellTreinamento = row.insertCell();
            const cellData = row.insertCell();
            const cellArquivo = row.insertCell();
            const cellConcluido = row.insertCell();

            cellUsuario.textContent = treinamento.usuario;
            cellTreinamento.textContent = treinamento.treinamento;
            cellData.textContent = treinamento.data;
            cellArquivo.innerHTML = treinamento.arquivo ? `<a href="${treinamento.arquivo}" target="_blank">Ver Arquivo</a>` : 'Nenhum Arquivo';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = treinamento.concluido;
            checkbox.addEventListener('change', () => {
                treinamento.concluido = checkbox.checked;
                saveData();
                updateGrafico();
            });
            cellConcluido.appendChild(checkbox);
        });

        document.getElementById('prev-tabela').disabled = paginaTabela === 0;
        document.getElementById('next-tabela').disabled = end >= treinamentos.length;
    }

    function updateGrafico() {
        const labels = usuarios;
        const dadosConcluidos = usuarios.map(usuario => {
            return treinamentos.filter(t => t.usuario === usuario && t.concluido).length;
        });
        const dadosNaoConcluidos = usuarios.map(usuario => {
            return treinamentos.filter(t => t.usuario === usuario && !t.concluido).length;
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Concluído',
                    data: dadosConcluidos,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }, {
                    label: 'Não Concluído',
                    data: dadosNaoConcluidos,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    formCadastro.addEventListener('submit', (e) => {
        e.preventDefault();
        const nome = document.getElementById('nome').value;

        if (nome && !usuarios.includes(nome)) {
            usuarios.push(nome);
            saveData();
            updateUsuarioSelect();
            updateUsuarioList();
            updateGrafico();
            formCadastro.reset();
        }
    });

    formNovoTreinamento.addEventListener('submit', (e) => {
        e.preventDefault();
        const novoTreinamento = document.getElementById('novo-treinamento').value;

        if (novoTreinamento && !tiposTreinamento.includes(novoTreinamento)) {
            tiposTreinamento.push(novoTreinamento);
            saveData();
            updateTreinamentoSelect();
            formNovoTreinamento.reset();
        }
    });

    formTreinamento.addEventListener('submit', (e) => {
        e.preventDefault();
        const usuario = usuarioSelect.value;
        const treinamento = treinamentoSelect.value;
        const data = document.getElementById('data').value;
        const arquivoInput = document.getElementById('arquivo');
        const arquivo = arquivoInput.files[0] ? URL.createObjectURL(arquivoInput.files[0]) : null;

        if (usuario && treinamento && data) {
            treinamentos.push({
                usuario,
                treinamento,
                data,
                arquivo,
                concluido: false // Novo treinamento inicia como não concluído
            });
            saveData();
            updateTabelaTreinamentos();
            updateGrafico();
            formTreinamento.reset();
        }
    });

    document.getElementById('prev-usuarios').addEventListener('click', () => {
        if (paginaUsuarios > 0) {
            paginaUsuarios--;
            updateUsuarioList();
        }
    });

    document.getElementById('next-usuarios').addEventListener('click', () => {
        if ((paginaUsuarios + 1) * usuariosPorPagina < usuarios.length) {
            paginaUsuarios++;
            updateUsuarioList();
        }
    });

    document.getElementById('prev-tabela').addEventListener('click', () => {
        if (paginaTabela > 0) {
            paginaTabela--;
            updateTabelaTreinamentos();
        }
    });

    document.getElementById('next-tabela').addEventListener('click', () => {
        if ((paginaTabela + 1) * tabelaPorPagina < treinamentos.length) {
            paginaTabela++;
            updateTabelaTreinamentos();
        }
    });

    // Inicializa a página com os dados existentes
    updateUsuarioSelect();
    updateTreinamentoSelect();
    updateUsuarioList();
    updateTabelaTreinamentos();
    updateGrafico();
});

