from django.shortcuts import render
from mailings.models import Mailing
from clients.models import Recipient


def dashboard(request):
    mailings = Mailing.objects.all()
    total_mailings = mailings.count()
    active_mailings = mailings.filter(status='started').count()
    # уникальные получатели только среди тех, кто включён в рассылки
    unique_recipients = Recipient.objects.filter(mailings__in=mailings).distinct().count()

    context = {
        'total_mailings': total_mailings,
        'active_mailings': active_mailings,
        'unique_recipients': unique_recipients,
    }
    return render(request, 'dashboard.html', context)
