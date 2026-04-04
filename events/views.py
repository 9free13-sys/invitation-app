from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Event
from guests.models import Guest
import uuid


def create_event(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        event_type = request.POST.get('event_type')
        custom_event_type = request.POST.get('custom_event_type')
        date = request.POST.get('date')
        location = request.POST.get('location')
        description = request.POST.get('description')
        allowed_companions = request.POST.get('allowed_companions') or 0

        if event_type == 'outro' and custom_event_type:
            event_type = custom_event_type

        event = Event.objects.create(
            name=name,
            event_type=event_type,
            date=date,
            location=location,
            description=description,
            allowed_companions=int(allowed_companions),
            owner=request.user if request.user.is_authenticated else None
        )

        if not request.user.is_authenticated:
            request.session['pending_event_id'] = event.id

        return redirect('event_detail', event_id=event.id)

    return render(request, 'create_invite.html')


def event_list(request):
    events = Event.objects.filter(owner=request.user).order_by('-date')
    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    pending_event_id = request.session.get('pending_event_id')

    if event.owner:
        if not request.user.is_authenticated or event.owner != request.user:
            return redirect('/login/')
    else:
        if pending_event_id != event.id:
            return redirect('/login/')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        Guest.objects.create(
            event=event,
            full_name=full_name,
            phone=phone,
            email=email,
            token=uuid.uuid4()
        )

        return redirect(f'/event/{event.id}/?guest_added=1')

    guests = Guest.objects.filter(event=event)

    total_guests = guests.count()
    confirmed_guests = guests.filter(status='confirmado').count()
    pending_guests = guests.filter(status='pendente').count()
    declined_guests = guests.filter(status='recusado').count()

    if total_guests > 0:
        percentage = round((confirmed_guests / total_guests) * 100, 1)
    else:
        percentage = 0

    return render(request, 'events/event_detail.html', {
        'event': event,
        'guests': guests,
        'total_guests': total_guests,
        'confirmed_guests': confirmed_guests,
        'pending_guests': pending_guests,
        'declined_guests': declined_guests,
        'percentage': percentage,
    })


def _get_filtered_guests(request, event):
    guests = Guest.objects.filter(event=event)

    status_filter = request.GET.get('status', '').strip()
    companion_filter = request.GET.get('companion', '').strip()
    search_query = request.GET.get('q', '').strip()

    if status_filter in ['confirmado', 'pendente', 'recusado']:
        guests = guests.filter(status=status_filter)

    if companion_filter == 'with':
        guests = guests.exclude(companion_name__isnull=True).exclude(companion_name__exact='')
    elif companion_filter == 'without':
        guests = guests.filter(companion_name__isnull=True) | guests.filter(companion_name__exact='')

    if search_query:
        guests = guests.filter(full_name__icontains=search_query)

    guests = guests.order_by('full_name')

    return guests, status_filter, companion_filter, search_query


def event_guests(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if not request.user.is_authenticated:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect('login')

    if event.owner != request.user:
        messages.error(request, "Não tens permissão para ver os convidados deste evento.")
        return redirect('event_list')

    guests, status_filter, companion_filter, search_query = _get_filtered_guests(request, event)

    context = {
        'event': event,
        'guests': guests,
        'status_filter': status_filter,
        'companion_filter': companion_filter,
        'search_query': search_query,
    }
    return render(request, 'events/event_guests.html', context)


def export_guests_excel(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if not request.user.is_authenticated:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect('login')

    if event.owner != request.user:
        messages.error(request, "Não tens permissão para exportar esta lista.")
        return redirect('event_list')

    guests, status_filter, companion_filter, search_query = _get_filtered_guests(request, event)

    wb = Workbook()
    ws = wb.active
    ws.title = "Convidados"

    headers = ["Nome", "Telefone", "Email", "Estado"]
    if event.allowed_companions > 0:
        headers.append("Acompanhante")

    ws.append(headers)

    for guest in guests:
        row = [
            guest.full_name,
            guest.phone or "",
            guest.email or "",
            guest.status,
        ]
        if event.allowed_companions > 0:
            row.append(guest.companion_name or "")
        ws.append(row)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="convidados_evento_{event.id}.xlsx"'

    wb.save(response)
    return response


def export_guests_pdf(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if not request.user.is_authenticated:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect('login')

    if event.owner != request.user:
        messages.error(request, "Não tens permissão para exportar esta lista.")
        return redirect('event_list')

    guests, status_filter, companion_filter, search_query = _get_filtered_guests(request, event)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="convidados_evento_{event.id}.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Lista de Convidados - {event.name}", styles["Title"]))
    elements.append(Spacer(1, 12))

    info_lines = [
        f"Data: {event.date}",
        f"Local: {event.location or 'Não informado'}",
        f"Tipo de evento: {event.event_type_label}",
    ]

    if event.allowed_companions > 0:
        info_lines.append(f"Acompanhantes permitidos por convite: {event.allowed_companions}")
    else:
        info_lines.append("Acompanhantes: Não permitidos")

    if status_filter:
        info_lines.append(f"Filtro por estado: {status_filter}")
    if companion_filter == 'with':
        info_lines.append("Filtro por acompanhante: com acompanhante")
    elif companion_filter == 'without':
        info_lines.append("Filtro por acompanhante: sem acompanhante")
    if search_query:
        info_lines.append(f"Pesquisa: {search_query}")

    for line in info_lines:
        elements.append(Paragraph(line, styles["Normal"]))

    elements.append(Spacer(1, 16))

    if event.allowed_companions > 0:
        data = [["Nome", "Acompanhante", "Telefone", "Email", "Estado"]]
        for guest in guests:
            data.append([
                guest.full_name,
                guest.companion_name or "-",
                guest.phone or "-",
                guest.email or "-",
                guest.status.capitalize(),
            ])
        col_widths = [130, 130, 90, 120, 70]
    else:
        data = [["Nome", "Telefone", "Email", "Estado"]]
        for guest in guests:
            data.append([
                guest.full_name,
                guest.phone or "-",
                guest.email or "-",
                guest.status.capitalize(),
            ])
        col_widths = [170, 110, 150, 80]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 16))

    total_guests = guests.count()
    confirmed_guests = guests.filter(status='confirmado').count()
    pending_guests = guests.filter(status='pendente').count()
    declined_guests = guests.filter(status='recusado').count()

    summary = [
        f"Total de convidados na lista filtrada: {total_guests}",
        f"Confirmados: {confirmed_guests}",
        f"Pendentes: {pending_guests}",
        f"Recusados: {declined_guests}",
    ]

    for line in summary:
        elements.append(Paragraph(line, styles["Normal"]))

    doc.build(elements)
    return response


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if not request.user.is_authenticated:
        messages.error(request, "Precisas de iniciar sessão.")
        return redirect('login')

    if event.owner != request.user:
        messages.error(request, "Não tens permissão para eliminar este evento.")
        return redirect('event_list')

    event.delete()
    messages.success(request, "Evento eliminado com sucesso!")
    return redirect('event_list')