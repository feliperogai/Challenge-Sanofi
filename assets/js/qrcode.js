document.addEventListener('DOMContentLoaded', (event) => {
    // Preencher o campo de data e hora com o valor atual
    const dateField = document.getElementById('date');
    const now = new Date();
    const formattedDate = now.toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
    dateField.value = formattedDate;
});

function generateAndUploadPDF() {
    const { jsPDF } = window.jspdf;

    // Obter dados do formulário
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const date = document.getElementById('date').value;
    const signature = document.getElementById('signature').value;

    // Criar um novo PDF
    const doc = new jsPDF();
    doc.text(`Nome Completo: ${name}`, 10, 10);
    doc.text(`Email: ${email}`, 10, 20);
    doc.text(`Data e Hora: ${date}`, 10, 30);
    doc.text(`Assinatura: ${signature}`, 10, 40);

    // Salvar o PDF localmente
    doc.save('formulario.pdf');

    // Redirecionar para a página de confirmação
    window.location.href = "../pages/confirmation.html";
}

