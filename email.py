from datetime import date


def normalize_addresses(value: str) -> str:
    """Приводит email к нижнему регистру и убирает пробелы по краям."""
    return value.strip().lower()


def add_short_body(email: dict) -> dict:
    """Добавляет короткую версию тела письма (первые 10 символов + '...')."""
    body = email.get("body", "")
    email["short_body"] = (body[:10] + "...")
    return email


def clean_body_text(body: str) -> str:
    """Заменяет табы и переводы строк на пробелы."""
    return body.replace("\t", " ").replace("\n",
                                           " ").replace("\r", " ")


def build_sent_text(email: dict) -> str:
    """Формирует итоговый текст письма."""
    return (
        f"Кому: {email['recipient']}, от {email['masked_sender']}\n"
        f"Тема: {email['subject']}, дата {email['date']}\n"
        f"{email['body']}"
    )


def check_empty_fields(subject: str, body: str) -> tuple[bool, bool]:
    """Проверяет, пустые ли тема и тело."""
    return subject.strip() == "", body.strip() == ""


def mask_sender_email(login: str, domain: str) -> str:
    """Маскирует email: первые 2 символа + '***@' + домен."""
    if len(login) < 2:
        masked_login = login + "***"
    else:
        masked_login = login[:2] + "***"
    return f"{masked_login}@{domain}"


def get_correct_email(email_list: list[str]) -> list[str]:
    """Возвращает список корректных email: есть '@', домен
     .com/.ru/.net (регистронезависимо)."""
    valid_domains = {".com", ".ru", ".net"}
    correct = []
    for email in email_list:
        email = email.strip()
        if "@" not in email:
            continue
        parts = email.split("@")
        if len(parts) != 2:
            continue
        local, domain = parts
        if not local or not domain:
            continue
        # Проверяем домен (регистронезависимо)
        domain_lower = domain.lower()
        if any(domain_lower.endswith(d) for d in valid_domains):
            correct.append(email)
    return correct


def create_email(sender: str, recipient: str, subject: str, body: str) -> dict:
    """Создаёт базовое письмо."""
    return {
        "sender": sender,
        "recipient": recipient,
        "subject": subject,
        "body": body
    }


def add_send_date(email: dict) -> dict:
    """Добавляет текущую дату в формате YYYY-MM-DD."""
    email["date"] = str(date.today())
    return email


def extract_login_domain(address: str) -> tuple[str, str]:
    """Разделяет email на логин и домен."""
    address = address.strip()
    if "@" not in address:
        return "", ""
    login, domain = address.split("@", 1)
    return login, domain


def sender_email(recipient_list: list[str], subject: str, message: str, *,
                 sender="default@study.com") -> list[dict]:
    # 1. Проверить, что recipient_list не пустой
    if not recipient_list:
        return []

    # 2. Проверить корректность email
    all_emails = [sender] + recipient_list
    correct_emails = set(get_correct_email(all_emails))

    if sender not in correct_emails:
        return []  # отправитель некорректный

    valid_recipients = [r for r in recipient_list if r in correct_emails]

    # 3. Проверить пустоту темы и тела
    is_subject_empty, is_body_empty = check_empty_fields(subject, message)
    if is_subject_empty or is_body_empty:
        return []

    # 4. Исключить отправку самому себе
    valid_recipients = [r for r in valid_recipients if
                        normalize_addresses(r) != normalize_addresses(sender)]

    # 5. Нормализовать данные
    sender_norm = normalize_addresses(sender)
    subject_clean = clean_body_text(subject)
    body_clean = clean_body_text(message)
    recipients_norm = [normalize_addresses(r) for r in valid_recipients]

    emails = []
    for recipient in recipients_norm:
        # 6. Создать письмо
        email = create_email(sender_norm, recipient, subject_clean, body_clean)

        # 7. Добавить дату
        email = add_send_date(email)

        # 8. Замаскировать отправителя
        login, domain = extract_login_domain(sender_norm)
        email["masked_sender"] = mask_sender_email(login, domain)

        # 9. Короткое тело
        email = add_short_body(email)

        # 10. Итоговый текст
        email["sent_text"] = build_sent_text(email)

        emails.append(email)

    return emails


# Пример использования
test_emails = [
    "user@gmail.com",
    "admin@company.ru",
    "test_123@service.net",
    "Example.User@domain.com",
    "default@study.com",
    " hello@corp.ru  ",
    "user@site.NET",
    "user@domain.coM",
    "user.name@domain.ru",
    "usergmail.com",
    "user@domain",
    "user@domain.org",
    "@mail.ru",
    "name@.com",
    "name@domain.comm",
    "",
    "   ",
]

result = sender_email(
    recipient_list=test_emails,
    subject="Hello!",
    message="Привет, коллега!\nКак дела?\tВсё хорошо?"
)

for sent_email in result:
    print(sent_email["sent_text"])
    print("-" * 40)
