const now = new Date();
    const datetimeLocal = now.toISOString().slice(0, 16); // Formato: YYYY-MM-DDTHH:MM
    document.getElementById('date').value = datetimeLocal;
    document.getElementById('current_date').value = now.toISOString(); // Para enviar a data atual

