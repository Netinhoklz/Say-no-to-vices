document.addEventListener('DOMContentLoaded', () => {
    const calendarGrid = document.getElementById('recaida-calendar');
    const hiddenInput = document.getElementById('recaida_dates');
    const mainForm = document.getElementById('user-form');

    if (!calendarGrid || !hiddenInput || !mainForm) {
        console.error("Elementos essenciais do formulário de calendário não encontrados.");
        return;
    }

    const today = new Date();
    const days = [];
    const weekdays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

    // 1. Adicionar cabeçalhos dos dias da semana
    weekdays.forEach(day => {
        const weekdayHeader = document.createElement('div');
        weekdayHeader.classList.add('calendar-header');
        weekdayHeader.textContent = day;
        calendarGrid.appendChild(weekdayHeader);
    });

    // 2. Gerar os últimos 30 dias
    for (let i = 0; i < 30; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        days.push(date);
    }
    days.reverse(); // Mostrar do mais antigo para o mais recente

    // 3. Adicionar espaçadores para alinhar o primeiro dia
    const firstDay = days[0];
    // getDay() retorna 0 para Domingo, 1 para Segunda, etc.
    const startingDayOfWeek = firstDay.getDay();

    for (let i = 0; i < startingDayOfWeek; i++) {
        const spacer = document.createElement('div');
        spacer.classList.add('calendar-spacer');
        calendarGrid.appendChild(spacer);
    }

    // 4. Preencher o grid do calendário com os dias
    days.forEach(date => {
        const dayContainer = document.createElement('div');
        dayContainer.classList.add('calendar-day', 'clean'); // Começa como 'limpo' (verde)

        const dateString = date.toISOString().split('T')[0]; // Formato YYYY-MM-DD

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `day-${dateString}`;
        checkbox.name = 'recaida_day';
        checkbox.value = dateString;
        checkbox.style.display = 'none'; // Escondemos o checkbox real

        const label = document.createElement('label');
        label.htmlFor = `day-${dateString}`;
        label.textContent = date.getDate().toString().padStart(2, '0'); // Mostra apenas o dia, ex: '07'

        dayContainer.appendChild(checkbox);
        dayContainer.appendChild(label);
        calendarGrid.appendChild(dayContainer);

        // Adiciona o evento de clique para alternar o estado
        dayContainer.addEventListener('click', () => {
            checkbox.checked = !checkbox.checked;
            dayContainer.classList.toggle('clean');
            dayContainer.classList.toggle('recaida');
        });
    });

    // Antes de enviar o formulário, coletar as datas marcadas
    mainForm.addEventListener('submit', (event) => {
        const selectedDates = [];
        const checkedBoxes = calendarGrid.querySelectorAll('input[type="checkbox"]:checked');

        checkedBoxes.forEach(box => {
            selectedDates.push(box.value);
        });

        // Salva as datas no campo oculto, separadas por ponto e vírgula
        hiddenInput.value = selectedDates.join(';');
    });
});