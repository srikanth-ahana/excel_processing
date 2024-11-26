from .models import ProcessedData
from django.shortcuts import redirect, render
from django.shortcuts import render, redirect, HttpResponse
from .forms import UploadFileForm
from .models import ProcessedData, UploadedFile, VendorTemplate, ArrivalTemplate
import pandas as pd
import re, os
from django.conf import settings
from django.contrib import messages



def delete_old_files():
    """
    Deletes all files in the MEDIA_ROOT directory.
    """
    media_dir = settings.MEDIA_ROOT
    uploads_dir = os.path.join(media_dir, 'uploads')
    print('media_dir',uploads_dir)
    for filename in os.listdir(uploads_dir):
        file_path = os.path.join(uploads_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")


def compare_lists(request, list1, list2):
    list1 = []
    list2 = []


def upload_file1(request):
    """
    Business Logic
    """
    try:
        is_arr_matched = False
        is_ven_matched = False
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file_instance = form.save()  # Save the file and get the instance
                file_name = uploaded_file_instance.file.name  # Get the file name
                filename2 = uploaded_file_instance.file2.name

                # Read the Excel files
                arr_file = pd.read_excel(file_name, sheet_name='Arrivals')
                vendor_file = pd.read_excel(filename2)
                arr_file_header = arr_file.columns.tolist()
                vendor_file_header = vendor_file.columns.tolist()
                vendor_modal_header = list(VendorTemplate.objects.values(
                    'template_name', 'guest_name', 'is_merged', 'arr_date_name', 'dept_date_name', 'arr_dept_date_name', 'amount_name'))
                arr_modal_header = list(ArrivalTemplate.objects.values(
                    'name', 'is_merged', 'arr_date_name', 'dept_date_name', 'arr_dept_date_name', 'rate_amt_name_name'))

                # Select the 'NAME' column and process names
                selected_column = arr_file['NAME']
                processed_names = []

                # Define a pattern for junk titles (e.g., Mr., Mrs., etc.)
                junk_titles_pattern = r'\b(Mr|Mrs|Ms|Dr|Prof)\.?\b|\*'

                # Clear previous data
                ProcessedData.objects.all().delete()

                for index, name in enumerate(selected_column):
                    # Clean up the name
                    cleaned_name = re.sub(
                        junk_titles_pattern, '', name, flags=re.IGNORECASE)
                    # Replace commas with spaces
                    cleaned_name = re.sub(r',', ' ', cleaned_name)
                    cleaned_name = re.sub(
                        r'\.', '', cleaned_name)  # Remove periods

                    # Split, reverse the first two words if possible, and rejoin
                    words = cleaned_name.strip().split()
                    if len(words) >= 2:
                        words[0], words[1] = words[1], words[0]
                    reversed_name = " ".join(words)

                    # Add the processed name to the list
                    processed_names.append(reversed_name)

                    # Search for the processed name in the second DataFrame (vendor_file)
                    matched_row = vendor_file[vendor_file['Guest Name']
                                              == reversed_name]

                    # Get the rate_amt from arr_file if available
                    rate_amt = arr_file.at[index,
                                           'RATE_AMT'] if 'RATE_AMT' in arr_file.columns else 0

                    if not matched_row.empty:
                        commission = matched_row['Total Invoice Value'].values[0]
                        rate_amd = rate_amt  # Add rate_amt to rate_amd
                        # Example calculation (adjust if needed)
                        difference = commission - rate_amt
                        is_matched_data = True
                    else:
                        commission = 0
                        rate_amd = rate_amt  # Set rate_amt if no match is found
                        difference = 0
                        is_matched_data = False

                    # Save processed data into the database
                    ProcessedData.objects.create(
                        guest_name=reversed_name,
                        commission=commission,
                        rate_amd=rate_amd,
                        difference=difference,
                        is_matched=is_matched_data
                    )

                return redirect('success')  # Redirect after successful upload
        else:
            form = UploadFileForm()
        return render(request, 'file_handler/upload.html', {'form': form})
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")


def upload_file(request):
    """
    Business Logic
    """
    try:
        is_arr_matched = False
        is_ven_matched = False
                
        if request.method == 'POST':
            delete_old_files()
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                
                uploaded_file_instance = form.save()  # Save the file and get the instance
                # file_name = uploaded_file_instance.file.name  # Get the file name
                # filename2 = uploaded_file_instance.file2.name
                file_name = os.path.join(settings.MEDIA_ROOT, uploaded_file_instance.file.name)
                file_name2 = os.path.join(settings.MEDIA_ROOT, uploaded_file_instance.file2.name)

                # Read the Excel files
                arr_file = pd.read_excel(file_name, sheet_name='Arrivals')
                vendor_file = pd.read_excel(file_name2)
                arr_file_header = arr_file.columns.tolist()
                vendor_file_header = vendor_file.columns.tolist()

                # Get modal headers
                arr_modal_headers_true = list(ArrivalTemplate.objects.filter(is_merged=True).values(
                    'name', 'arr_dept_date_name', 'rate_amt_name_name'))
                arr_modal_headers_false = list(ArrivalTemplate.objects.filter(is_merged=False).values(
                    'name', 'arr_date_name', 'dept_date_name', 'rate_amt_name_name'))
                vendor_modal_headers_true = list(VendorTemplate.objects.filter(is_merged=True).values(
                    'guest_name', 'arr_dept_date_name', 'amount_name'))
                vendor_modal_headers_false = list(VendorTemplate.objects.filter(is_merged=False).values(
                    'guest_name', 'arr_date_name', 'dept_date_name', 'amount_name'))
                # for arr in arr_modal_headers_true:
                # print(arr_file_header)
                arr_modal_queryset = arr_modal_headers_true + arr_modal_headers_false
                arr_modal_headers = [list(item.values()) for item in arr_modal_queryset]
                vendor_modal_queryset = vendor_modal_headers_true + vendor_modal_headers_false
                vendor_modal_headers = [list(item.values()) for item in vendor_modal_queryset]
                arr_subsets = [sublist for sublist in arr_modal_headers if set(sublist).issubset(set(arr_file_header))]
                ven_subsets = [sublist for sublist in vendor_modal_headers if set(sublist).issubset(set(vendor_file_header))]

                # Output results
                if ven_subsets:
                    ven_matched = []
                    for item in ven_subsets:
                        if set(item[2:]).issubset(vendor_file_header):
                            ven_matched.append(item)
                    is_ven_matched = True

                if arr_subsets:
                    arr_matched = []
                    for item in arr_subsets:
                        if set(item[2:]).issubset(arr_file_header):
                            arr_matched.append(item)
                    is_arr_matched = True
                
                # return

                if not (is_ven_matched):
                    messages.error(request,"Vendor Headers do not match with the modal templates!")
                    return render(request, 'file_handler/upload.html', {'form': form})
                if not (is_arr_matched):
                    messages.error(request,"Arrival Headers do not match with the modal templates!")
                    return render(request, 'file_handler/upload.html', {'form': form})

                # Proceed with processing only if headers matched
                selected_column = arr_file[arr_matched[0][0]]
                processed_names = []

                # Define a pattern for junk titles (e.g., Mr., Mrs., etc.)
                junk_titles_pattern = r'\b(Mr|Mrs|Ms|Dr|Prof)\.?\b|\*'

                # Clear previous data
                ProcessedData.objects.all().delete()

                for index, name in enumerate(selected_column):
                    # Clean up the name
                    cleaned_name = re.sub(
                        junk_titles_pattern, '', name, flags=re.IGNORECASE)
                    # Replace commas with spaces
                    cleaned_name = re.sub(r',', ' ', cleaned_name)
                    cleaned_name = re.sub(
                        r'\.', '', cleaned_name)  # Remove periods

                    # Split, reverse the first two words if possible, and rejoin
                    words = cleaned_name.strip().split()
                    if len(words) >= 2:
                        words[0], words[1] = words[1], words[0]
                    reversed_name = " ".join(words)

                    # Add the processed name to the list
                    processed_names.append(reversed_name)

                    # Search for the processed name in the second DataFrame (vendor_file)
                    matched_row = vendor_file[vendor_file[ven_matched[0][0]]
                                              == reversed_name]

                    # Get the rate_amt from arr_file if available
                    rate_amt = arr_file.at[index,
                                            arr_matched[0][3]] if arr_matched[0][3] in arr_file.columns else 0
                    rate_amt_difference = rate_amt * 0.10
                    # print(rate_amt)
                    # return
                    # print('here')
                    if not matched_row.empty:
                        commission = matched_row[ven_matched[0][-1]].values[0]
                        rate_amd = rate_amt  # Add rate_amt to rate_amd
                        # Example calculation (adjust if needed)
                        difference = rate_amt_difference
                        is_matched_data = True
                    else:
                        commission = 0
                        rate_amd = rate_amt  # Set rate_amt if no match is found
                        difference = 0
                        is_matched_data = False
                    # return
                    # Save processed data into the database
                    ProcessedData.objects.create(
                        guest_name=reversed_name,
                        commission=commission,
                        rate_amd=rate_amd,
                        difference=difference,
                        is_matched=is_matched_data
                    )

                return redirect('success')  # Redirect after successful upload
        else:
            form = UploadFileForm()
        return render(request, 'file_handler/upload.html', {'form': form})
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")


def success(request):
    """
    Table Display Page
    """
    try:
        MatchedData = ProcessedData.objects.filter(is_matched=True).all().order_by(
            '-is_matched')  # Fetch data from the database
        TotalMatched = ProcessedData.objects.filter(is_matched=True).all().count()
        UnmatchedData = ProcessedData.objects.filter(is_matched=False).all().order_by(
            '-is_matched')  # Fetch data from the database
        TotalUnmatched = ProcessedData.objects.filter(is_matched=False).all().count()
        SumCommission = list(ProcessedData.objects.filter(is_matched=True).values('commission'))
        total_commission = sum(item['commission'] for item in SumCommission)
        return render(request, 'file_handler/success.html', {'data': MatchedData, 'unmatched_data': UnmatchedData,'m_total':TotalMatched,'um_total':TotalUnmatched, 'total_commission':total_commission})
    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")


"""
arr_file_header ['ROOM_NO', 'NAME', 'Result', 'Result2', 'COMPANY', 'ARR DATE', 'DEP_DATE', 'ROOM TYPE', 'ADULT', 'CHILD', 'ROOMS', 'MKT_CODE', 'RESV_STATUS', 'RATE_CODE', 'CURRENCY', 'RATE_AMT', 'ETD', 'RESV_COMMENTS', 'NOTES']

vendor_file_header ['Booking ID', 'CheckIn - CheckOut Date', 'Commission Invoice No', 'Guest Name', 'PNR', 'Vendor No', 'HotelName', 'Hotel Code', 'Company Code', 'Commission', 'PLB/VDI Income', 'CGST/SGST', 'IGST_', 'Total Invoice Value', 'Unnamed: 14', 'RATE from Arrivals', 'Total AMT from arrivals']

vendor_modal_header [{'template_name': 'MMT', 'guest_name': 'Guest Name', 'is_merged': True, 'arr_date_name': None, 'dept_date_name': None, 'arr_dept_date_name': 'CheckIn - CheckOut Date', 'amount_name': 'Total Invoice Value'}, {'template_name': 'Booking.com', 'guest_name': 'Guest Name', 'is_merged': True, 'arr_date_name': None, 'dept_date_name': None, 'arr_dept_date_name': 'CheckIn - CheckOut Date', 'amount_name': 'Total Invoice Value'}]

arr_modal_header [{'name': 'Name', 'is_merged': False, 'arr_date_name': 'ARR DATE', 'dept_date_name': 'DEP_DATE', 'arr_dept_date_name': None, 'rate_amt_name_name': 'RATE_AMT'}]

Vender Matched lists from b: ['Guest Name', 'CheckIn - CheckOut Date', 'Total Invoice Value']

Arrival Matched lists from b: ['NAME', 'ARR DATE', 'DEP_DATE', 'RATE_AMT']
"""
