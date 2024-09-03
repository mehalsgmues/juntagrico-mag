import csv
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from ..forms import CSVUploadForm, CSVSelectionForm
from ..models import MapJob


def import_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            csv_data = [line for line in csv.reader(decoded_file) if len(line) >= 2 and line[0].startswith('POLYGON')]

            request.session['csv_data'] = csv_data  # Save CSV data to session for the next view
            return redirect(reverse('mapjob:select_entries'))
    else:
        form = CSVUploadForm()
    return render(request, 'admin/mapjob/mapjob/import_csv.html', {'form': form})


def select_entries(request):
    csv_data = request.session.get('csv_data', [])

    if not csv_data:
        messages.error(request, "No CSV data found in session.")
        return redirect(reverse('mapjob:import'))

    if request.method == 'POST':
        form = CSVSelectionForm(request.POST, csv_data=csv_data)
        if form.is_valid():
            inst = form.instance
            selected_entries = []
            for i, row in enumerate(csv_data):
                if form.cleaned_data.get(f'select_{i}'):
                    # Process selected rows
                    instance = MapJob.objects.create(
                        geo_area={
                            "type": "Feature",
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [[point.split(' ') for point in row[0][10:-2].split(', ')]]
                            },
                            "properties": {
                                "name": row[1] if len(row) > 1 else "",
                                "description": row[2] if len(row) > 2 else "",
                            }
                        },
                        type=inst.type,
                        slots=inst.slots,
                        infinite_slots=inst.infinite_slots,
                        time=inst.time,
                        multiplier=inst.multiplier,
                        additional_description=inst.additional_description,
                        duration_override=inst.duration_override,
                    )
                    selected_entries.append(instance)

            messages.success(request, f"{len(selected_entries)} entries were successfully created.")
            return redirect(reverse('admin:mapjob_mapjob_changelist'))
    else:
        form = CSVSelectionForm(csv_data=csv_data)

    return render(request, 'admin/mapjob/mapjob/select_entries.html', {'form': form, 'csv_data': csv_data})
