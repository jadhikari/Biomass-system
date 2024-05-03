import io
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from projects.models import Projects
from .models import DeliveryRecord
from wood_type.models import WoodType
from vendor.models import WoodSupplier, WoodSource
from .wsl_utils_views import filter_wood_scaling_data, paginate_wood_scaling_data, calculate_totals
from .pdf_utils_views import generate_pdf, download_certificate, pdf_data
from .forms import UploadFileForm, DeliverySearchForm, RemarksForm, GraphSearchForm
import pandas as pd
from io import StringIO 
import csv
import chardet
from datetime import datetime
from plotly.offline import plot
import plotly.graph_objs as go
from collections import defaultdict


from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from .signals import non_duplicate_data_uploaded

@login_required
@permission_required('wood_delivery.view_deliveryrecord', raise_exception=True)
def index(request):
    all_wood_scaling_data = DeliveryRecord.objects.all()

    # Retrieve search parameters
    project_id = request.GET.get('project_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    vendor_name = request.GET.get('vendor_name')
    wood_source = request.GET.get('wood_source')

    # Filter data based on search parameters
    error_message = None
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if end_date < start_date:
            error_message = "End date must be equal to or later than the start date"

    # If there's an error, display an alert and return
    if error_message:
        return render(request, 'wood_scaling/wood_scaling_list.html', {'error_message':f"{str(error_message)}: Click reset button "})

    # Filter data based on search parameters
    filtered_wood_scaling_data = filter_wood_scaling_data(all_wood_scaling_data, start_date, end_date, project_id, vendor_name, wood_source)
    filtered_wood_scaling_data = sorted(filtered_wood_scaling_data, key=lambda x: x.id, reverse=True)

    # Download Excel file
    if request.GET.get('download') == 'excel':
        # Define the columns to be included in the excel file
        columns = ['id', 'project_id','weighing_day', 'slip_no', 'woods_type', 'trucks_num', 'wood_supplier', 'wood_sources', 'others',
           'total_weight_time', 'total_weight', 'empty_weight_time', 'empty_weight', 'net_weight', 'remarks']

        # Create an empty Pandas DataFrame with the specified columns
        rows = []

        # Iterate over filtered_wood_scaling_data and append rows to the DataFrame
        for data in filtered_wood_scaling_data:
            row = {
                'id': data.id,
                'project_id': data.project.project_id,
                'weighing_day': data.weighing_day,
                'slip_no': data.slip_no,
                'woods_type': data.woods_type.wood_name,
                'trucks_num': data.trucks_num,
                'wood_supplier': data.wood_supplier.name,
                'wood_sources': data.wood_sources.location,
                'others': data.wood_sources.registration_name,
                'total_weight_time': data.total_weight_time,
                'total_weight': data.total_weight,
                'empty_weight_time': data.empty_weight_time,
                'empty_weight': data.empty_weight,
                'net_weight': data.net_weight,
                'remarks': data.remarks,
                
            }
            
            # Append the row to the DataFrame
            rows.append(row)

        # Create a DataFrame from the list of rows
        df = pd.DataFrame(rows, columns=columns)

        # Create an in-memory buffer for the Excel file
        excel_buffer = io.BytesIO()

        # Use pandas to_excel to write the DataFrame to the buffer
        df.to_excel(excel_buffer, index=False)

        # Seek to the beginning of the buffer
        excel_buffer.seek(0)
        # Create a response with the CSV file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=filtered_wood_scaling_data.xlsx'
        response.write(excel_buffer.getvalue())

        return response

    # Pagination
    wood_scaling_data = paginate_wood_scaling_data(request, filtered_wood_scaling_data)

    # Calculate totals
    total_weight_sum, empty_weight_sum, corrected_net_sum, grand_total_weight_sum, grand_empty_weight_sum, grand_corrected_net_sum = calculate_totals(all_wood_scaling_data, wood_scaling_data)
    
    #geting the search from
    wood_scaling_search_form = DeliverySearchForm(request.GET)

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Woods Delivery List'},  # Replace with the actual URL for the 'Event' page
    ]
    context = {
        'wood_scaling_data': wood_scaling_data,
        'total_weight_sum': total_weight_sum,
        'empty_weight_sum': empty_weight_sum,
        'corrected_net_sum': corrected_net_sum,
        'grand_total_weight_sum': grand_total_weight_sum,
        'grand_empty_weight_sum': grand_empty_weight_sum,
        'grand_corrected_net_sum': grand_corrected_net_sum,
        'start_date': start_date,
        'end_date': end_date,
        'vendor_name': vendor_name,
        'wood_source': wood_source,
        'project_id' : project_id,
        'wood_scaling_search_form': wood_scaling_search_form ,
        'error_message': error_message ,
        'breadcrumbs': breadcrumbs,
    }



    return render(request, 'wood_delivery/index.html', context)
    
    

@login_required
@permission_required('wood_delivery.add_deliveryrecord', raise_exception=True)
def upload_csv(request):
    template_name = 'wood_delivery/upload_csv.html'
    success = False
    error_message = None

    if request.method == 'GET':
        form = UploadFileForm()
    elif request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Handle file upload and data processing
                csv_file = request.FILES['file']

                # Automatically detect the encoding
                rawdata = csv_file.read()
                result = chardet.detect(rawdata)
                encoding = result['encoding']

                # Decode the content using the detected encoding
                decoded_content = rawdata.decode(encoding)

                # Create a StringIO object to simulate a file-like object
                text_file = StringIO(decoded_content)

                # Read CSV file starting from the second line
                df = pd.read_csv(text_file, skiprows=[0])

                # Mapping between Japanese and English column names
                column_mapping = {
                    '計量日': 'weighing_day',
                    '伝票No.': 'slip_no',
                    '銘柄': 'woods_type',
                    '車番': 'trucks_num',
                    '業者': 'wood_supplier',
                    '行先': 'wood_sources',
                    '総重量時間': 'total_weight_time',
                    '総重量(kg)': 'total_weight',
                    '空重量時間': 'empty_weight_time',
                    '空重量(kg)': 'empty_weight',
                    '補正正味(kg)': 'net_weight',
                    '備考': 'remarks'
                }

                # Rename columns using the mapping
                df = df.rename(columns=column_mapping)

                # Specify the date format in the parse_dates parameter
                date_format = '%Y/%m/%d'

                # Check if 'weighing_day' is in the columns
                if 'weighing_day' in df.columns:
                    df['weighing_day'] = pd.to_datetime(df['weighing_day'], format=date_format)
                else:
                    raise ValueError("Column 'weighing_day' not found in the CSV file.")

                # Set user and project based on the current user
                df['user'] = request.user.username
                #df['project'] = form.cleaned_data['project_name'] # Assuming project_name is a ForeignKey in the form
                project_name_value = form.cleaned_data['project_name']
                if not (WoodSupplier.objects.filter(project=project_name_value).exists() & WoodSource.objects.filter(project=project_name_value).exists()):
                    raise ValueError(f"Error: Project '{project_name_value}' not found in both WoodSupplier and WoodSource tables.")

                df['project'] = project_name_value

                # Initialize lists to store duplicate, non-duplicate, and error rows
                duplicate_rows = []
                non_duplicate_rows = []
                error_rows = []
                
                # Iterate through rows and check for duplicates
                for index, row in df.iterrows():
                    # Handle 'woods_type' value
                    woods_type_value = row['woods_type']
                    wood_type_instance = WoodType.objects.filter(wood_id=woods_type_value).first()
                    # Check if WoodType instance exists
                    if wood_type_instance:
                        row['woods_type'] = wood_type_instance
                    else:
                        error_rows.append({"row_index": index, "column": "woods_type", "value": woods_type_value})
                        #continue  # Skip the row if WoodType instance is not found

                    # Handle 'wood_supplier' value
                    wood_supplier_value = row['wood_supplier']
                    wood_supplier_instance = WoodSupplier.objects.filter(project=row['project'], wood_supplier_id=wood_supplier_value).first()
                    
                    # Check if WoodSupplier instance exists
                    if wood_supplier_instance:
                        row['wood_supplier'] = wood_supplier_instance  # Assign the WoodSupplier instance itself
                    else:
                        error_rows.append({"row_index": index, "column": "wood_supplier", "value": wood_supplier_value})
                        #continue   # Skip the row if Woodsupplier instance is not found

                    # Handle 'wood_sources' value
                    wood_sources_value = row['wood_sources']
                    wood_source_instance = WoodSource.objects.filter(project=row['project'], wood_source_id=wood_sources_value).first()
                    
                    # Check if WoodSource instance exists
                    if wood_source_instance:
                        row['wood_sources'] = wood_source_instance  # Assign the WoodSource instance itself
                    else:
                        error_rows.append({"row_index": index, "column": "wood_sources", "value": wood_sources_value})
                        # continue                # Skip the row if WoodSource instance is not found

                    # Check for duplicates based on selected columns
                    existing_row = DeliveryRecord.objects.filter(
                        weighing_day=row['weighing_day'],
                        slip_no=row['slip_no'],
                        net_weight=row['net_weight'],
                        project=row['project']
                    ).first()
                    # If a match is found, add to duplicate_rows list; otherwise, add to non_duplicate_rows list
                    if existing_row:
                        duplicate_rows.append(row)
                    else:
                        non_duplicate_rows.append(row)
                # Print duplicate rows
                if duplicate_rows:
                    print("Duplicate rows:")
                    print(pd.DataFrame(duplicate_rows))
                    success = False
                    error_message = "Error: All data already exists. No data uploaded."
                # Print non-duplicate rows
                if non_duplicate_rows:
                    print("\nNon-duplicate rows:")
                    print(pd.DataFrame(non_duplicate_rows))

                    # Exclude unnamed columns before creating DeliveryRecord instances
                    relevant_columns = ['weighing_day', 'slip_no', 'woods_type', 'trucks_num', 'wood_supplier',
                                        'wood_sources', 'total_weight_time', 'total_weight', 'empty_weight_time',
                                        'empty_weight', 'net_weight', 'remarks', 'user', 'project']

                    delivery_records = [DeliveryRecord(**row[relevant_columns].to_dict()) for row in non_duplicate_rows]
                    DeliveryRecord.objects.bulk_create(delivery_records)


                    print("\nNon-duplicate rows successfully inserted into the database.")
                    success = True

                    pdf_data(delivery_records)
                    non_duplicate_data_uploaded.send(sender=None, non_duplicate_rows=delivery_records)

                # Print error rows
                if error_rows:
                    error_message = "Missing related instances. Cannot process the CSV data."
                # If all rows are unique, display success message
                if not duplicate_rows and not error_rows:
                    print("All data are unique. Upload successful.")
                    success = True
            except Exception as e:
                error_message = f"Error: {e}"
                print(f"Error reading or processing CSV file: {e}")

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Upload CSV'},
    ]

    context = {
        'form': form,
        'success': success,
        'error_message': error_message,
        'breadcrumbs': breadcrumbs
    }

    return render(request, template_name, context)




@login_required
def details_page(request, entry_id):
    entry = get_object_or_404(DeliveryRecord, id=entry_id)
    form = RemarksForm()

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Woods Delivery List', 'url': '/wood-delivery/'}, 
        {'name': f'Id {entry_id} Details'}, 
    ]

    # Pass all the data associated with the entry to the template
    context = {
        'entry': entry,
        'form': form,
        'breadcrumbs':breadcrumbs
    }
    if request.method == 'POST':
        form = RemarksForm(request.POST)
        if form.is_valid():
            entry.remarks = form.cleaned_data['remarks']

            # Convert request.user to a string
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            entry.by_user = user_string

            #entry.update_time = timezone.now()
            entry.save()
            return redirect('wood_delivery:details_page', entry_id=entry_id)
    else:
        # Pass the current value to the form
        form = RemarksForm(initial={'remarks': entry.remarks})

    return render(request, 'wood_delivery/details.html', context)


@login_required
def api_graph(request):
    # Retrieve all data
    all_wood_scaling_data = DeliveryRecord.objects.all()

    # Retrieve search parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter data based on search parameters
    error_message = None
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if end_date < start_date:
            error_message = "End date must be equal to or later than the start date"

    # If there's an error, display an alert and return
    if error_message:
        return render(request, 'wood_delivery/index.html', {'error_message': f"{str(error_message)}: Click reset button "})

    filters = {}
    if start_date and end_date:
        filters['weighing_day__range'] = [start_date, end_date]

    # Filter data based on search parameters
    filtered_wood_scaling_data = all_wood_scaling_data.filter(**filters)

    # Aggregate weights for each vendor on each day within each project
    project_vendor_day_weights = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    for entry in filtered_wood_scaling_data:
        project_vendor_day_weights[entry.project][entry.wood_supplier.name][entry.weighing_day] += entry.net_weight

    # Create traces for each vendor within each project
    data = []
    for project, vendor_day_weights in project_vendor_day_weights.items():
        for vendor_name, day_weights in vendor_day_weights.items():
            # Sort the day_weights dictionary based on keys (dates)
            sorted_weights = sorted(day_weights.items())

            # Unpack the sorted data
            sorted_dates, sorted_net_weights = zip(*sorted_weights)

            trace = go.Scatter(
                x=sorted_dates,
                y=sorted_net_weights,
                mode='lines+markers',
                name=f"{vendor_name} - {project}"  # Include project name in the legend
            )
            data.append(trace)
       
    # Calculate the start and end dates for the current month
    current_date = datetime.now().date()
    start_date = current_date.replace(day=1)
    end_date = pd.Timestamp(current_date).to_period('M').to_timestamp('M')

    # Layout for the graph
    layout = go.Layout(
        xaxis=dict(title='Weighing Day', type='date', range=[start_date, end_date]),
        yaxis=dict(title='Net Weight in KG'),
        showlegend=True,
        height=600,  # Set the desired height in pixels
        #width=800,   # Set the desired width in pixels
        xaxis_rangeslider_visible=True,
    )

    # Create the figure
    fig = go.Figure(data=data, layout=layout)

    # Convert the figure to HTML
    plot_div = plot(fig, output_type='div')

    # Getting the search form
    graph_search = GraphSearchForm(request.GET)

    breadcrumbs = [
        {'name': 'Home', 'url': '/welcome/'},
        {'name': 'Woods Delivery List', 'url': '/wood-delivery/'},
        {'name': 'Graph'},
    ]

    context = {
        'filtered_wood_scaling_data': filtered_wood_scaling_data,
        'graph_search': graph_search,
        'breadcrumbs': breadcrumbs,
        'plot_div': plot_div,  
    }
    return render(request, 'wood_delivery/graph.html', context)