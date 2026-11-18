from datetime import date, timedelta

def classify_vaccination(next_due_date, today=None):
    today = today or date.today()
    if not next_due_date:
        return "Sem data"
    due = date.fromisoformat(next_due_date)
    if due < today:
        return "Atrasada"
    if due <= today + timedelta(days=7):
        return "Próxima"
    return "Em dia"

def generate_reminder(person_name, vaccine, dose, next_due_date, status):
    if status == "Atrasada":
        return (f"Olá, {person_name}! A data prevista registrada para a dose {dose} da vacina "
                f"{vaccine} já passou ({next_due_date}). Entre em contato com a unidade de saúde "
                "para confirmar a situação e receber orientação.")
    if status == "Próxima":
        return (f"Olá, {person_name}! A próxima dose registrada para {vaccine} ({dose}) está "
                f"prevista para {next_due_date}. Consulte a unidade de saúde para confirmar a data.")
    if status == "Sem data":
        return (f"Olá, {person_name}! O registro de {vaccine} ({dose}) não possui uma próxima data. "
                "Consulte a unidade de saúde para verificar se há dose futura prevista.")
    return (f"Olá, {person_name}! Não há uma dose registrada para os próximos sete dias no sistema. "
            "Continue acompanhando sua caderneta e confirme as orientações com a unidade de saúde.")
