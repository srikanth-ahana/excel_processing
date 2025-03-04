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

"""
old file
def upload_file1(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded files to the model
            uploaded_file_instance = form.save()
            file_path1 = uploaded_file_instance.file.path
            file_path2 = uploaded_file_instance.file2.path

            # Read the uploaded Excel files
            vendor_file = pd.read_excel(file_path1, sheet_name='Arrivals')
            df2 = pd.read_excel(file_path2)

            # Process the 'NAME' column in the first file
            selected_column = vendor_file['NAME']
            junk_titles_pattern = r'\b(Mr|Mrs|Ms|Dr|Prof)\.?\b|\*'

            for name in selected_column:
                # Clean and process the name
                cleaned_name = re.sub(junk_titles_pattern, '', name, flags=re.IGNORECASE)
                cleaned_name = re.sub(r',', ' ', cleaned_name)
                cleaned_name = re.sub(r'\.', '', cleaned_name)

                # Reverse the first two words
                words = cleaned_name.strip().split()
                if len(words) >= 2:
                    words[0], words[1] = words[1], words[0]
                reversed_name = " ".join(words)

                # Search for the processed name in the second file
                matched_row = df2[df2['Guest Name'] == reversed_name]
                print('matched_row',matched_row)
                if not matched_row.empty:
                    commission = matched_row['Commission'].values[0]
                    rate_amd = matched_row['RATE_AMT'].values[0]
                    difference = rate_amd - commission
                else:
                    commission = 0
                    rate_amd = 0
                    difference = 0

                # Save processed data into the database
                ProcessedData.objects.create(
                    guest_name=reversed_name,
                    commission=commission,
                    rate_amd=rate_amd,
                    difference=difference
                )

            return redirect('success')  # Redirect to success page after processing

    else:
        form = UploadFileForm()
    return render(request, 'file_handler/upload.html', {'form': form})
def upload_file11(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file_instance = form.save()  # Save the file and get the instance
            file_name = uploaded_file_instance.file.name  # Get the file name
            filename2 = uploaded_file_instance.file2.name

            # Read the Excel files
            # arr_file = pd.read_excel("D:/BorderlessProject/media/" + file_name, sheet_name='Arrivals')
            # vendor_file = pd.read_excel("D:/BorderlessProject/media/" + filename2)  # Contains the data to retrieve
            arr_file = pd.read_excel(file_name, sheet_name='Arrivals')
            vendor_file = pd.read_excel(filename2)

            # Select the 'NAME' column and process names
            selected_column = arr_file['NAME']
            processed_names = []

            # Define a pattern for junk titles (e.g., Mr., Mrs., etc.)
            junk_titles_pattern = r'\b(Mr|Mrs|Ms|Dr|Prof)\.?\b|\*'

            # DataFrame to store the results
            result_data = []
            ProcessedData.objects.all().delete()  # Clear previous data

            for name in selected_column:
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
                search_word = reversed_name
                matched_row = vendor_file[vendor_file['Guest Name']
                                          == search_word]

                if not matched_row.empty:
                    commission = matched_row['Total Invoice Value'].values[0]
                    rate_amd = 0
                    difference = 0
                    is_matched_data = True
                else:
                    commission = 0
                    rate_amd = 0
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
"""



""" 
commission with arrival
"""
# with removed empty names
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
                print('arr_subsets',arr_subsets)
                print('ven_subsets',ven_subsets)
                # return
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
                # Proceed with processing only if headers matched
                selected_column = vendor_file[ven_matched[0][0]]
                print('selected_column', selected_column)

                processed_names = []

                # Define a pattern for junk titles (e.g., Mr., Mrs., etc.)
                junk_titles_pattern = r'\b(Mr|Mrs|Ms|Dr|Prof|⁰)\.?\b|\*'

                # Clear previous data
                ProcessedData.objects.all().delete()

                for index, name in enumerate(selected_column):
                    # Ensure 'name' is a string before processing
                    name = str(name).strip() if pd.notna(name) else ""

                    if not name:  # Skip empty guest names
                        continue

                    # Clean up the name
                    cleaned_name = re.sub(junk_titles_pattern, '', name, flags=re.IGNORECASE)
                    cleaned_name = re.sub(r',', ' ', cleaned_name)  # Replace commas with spaces
                    cleaned_name = re.sub(r'\.', '', cleaned_name)  # Remove periods

                    # Split, reverse the first two words if possible, and rejoin
                    words = cleaned_name.strip().split()
                    if len(words) >= 2:
                        words[0], words[1] = words[1], words[0]
                    reversed_name = " ".join(words).strip()

                    # Add the processed name to the list
                    processed_names.append(reversed_name)

                    # Search for the processed name in the second DataFrame (arr_file)
                    arr_file[arr_matched[0][0]] = arr_file[arr_matched[0][0]].fillna('').astype(str).str.lower().str.strip()
                    reversed_name = reversed_name.lower().strip()

                    # Normalize name for fuzzy matching
                    def normalize_name(name):
                        name = re.sub(r'[^\w\s]', '', name)  # Remove special characters
                        name = re.sub(r'\s+', ' ', name).strip()  # Remove extra spaces
                        name_words = name.lower().split()
                        return sorted(name_words)  # Sort words alphabetically for flexible matching
                    
                    if not reversed_name:  # Ensure non-empty reversed name
                        continue


                    reversed_normalized = normalize_name(reversed_name)

                    matched_row = arr_file[
                        arr_file[arr_matched[0][0]].apply(lambda x: all(word in x.lower() for word in reversed_normalized))
                    ]

                    # Get the rate_amt from vendor_file if available
                    rate_amt = vendor_file.at[index, ven_matched[0][3]] if ven_matched[0][3] in vendor_file.columns else 0
                    rate_amt_difference = rate_amt * 0.10

                    if not matched_row.empty:
                        commission = matched_row[arr_matched[0][-1]].values[0]
                        rate_amd = rate_amt  # Add rate_amt to rate_amd
                        difference = rate_amt_difference
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

# without removed empty names
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
                print('arr_subsets',arr_subsets)
                print('ven_subsets',ven_subsets)
                # return
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
                # Proceed with processing only if headers matched
                selected_column = vendor_file[ven_matched[0][0]]
                print('selected_column', selected_column)

                processed_names = []

                # Define a pattern for junk titles (e.g., Mr., Mrs., etc.)
                junk_titles_pattern = r'\b(Mr|Mrs|Ms|Dr|Prof|⁰)\.?\b|\*'

                # Clear previous data
                ProcessedData.objects.all().delete()

                for index, name in enumerate(selected_column):
                    # Ensure 'name' is a string before processing
                    name = str(name) if pd.notna(name) else ""

                    # Clean up the name
                    cleaned_name = re.sub(junk_titles_pattern, '', name, flags=re.IGNORECASE)
                    cleaned_name = re.sub(r',', ' ', cleaned_name)  # Replace commas with spaces
                    cleaned_name = re.sub(r'\.', '', cleaned_name)  # Remove periods

                    # Split, reverse the first two words if possible, and rejoin
                    words = cleaned_name.strip().split()
                    if len(words) >= 2:
                        words[0], words[1] = words[1], words[0]
                    reversed_name = " ".join(words)

                    # Add the processed name to the list
                    processed_names.append(reversed_name)

                    # Search for the processed name in the second DataFrame (arr_file)
                    arr_file[arr_matched[0][0]] = arr_file[arr_matched[0][0]].fillna('').astype(str).str.lower().str.strip()
                    reversed_name = reversed_name.lower().strip()

                    # Normalize name for fuzzy matching
                    def normalize_name(name):
                        name = re.sub(r'[^\w\s]', '', name)  # Remove special characters
                        name = re.sub(r'\s+', ' ', name).strip()  # Remove extra spaces
                        name_words = name.lower().split()
                        return sorted(name_words)  # Sort words alphabetically for flexible matching

                    reversed_normalized = normalize_name(reversed_name)

                    matched_row = arr_file[
                        arr_file[arr_matched[0][0]].apply(lambda x: all(word in x.lower() for word in reversed_normalized))
                    ]

                    # Get the rate_amt from vendor_file if available
                    rate_amt = vendor_file.at[index, ven_matched[0][3]] if ven_matched[0][3] in vendor_file.columns else 0
                    rate_amt_difference = rate_amt * 0.10

                    if not matched_row.empty:
                        commission = matched_row[arr_matched[0][-1]].values[0]
                        rate_amd = rate_amt  # Add rate_amt to rate_amd
                        difference = rate_amt_difference
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

"""
arrival with commission
"""
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
                print('arr_subsets',arr_subsets)
                print('ven_subsets',ven_subsets)
                # return
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
                junk_titles_pattern = r'\b(Mr|Mrs|Ms|Dr|Prof|⁰)\.?\b|\*'

                # Clear previous data
                ProcessedData.objects.all().delete()

                for index, name in enumerate(selected_column):
                    # Clean up the name
                    cleaned_name = re.sub(
                        junk_titles_pattern, '', name, flags=re.IGNORECASE)
                    # Replace commas with spaces
                    cleaned_name = re.sub(r',', ' ', cleaned_name)
                    cleaned_name = re.sub(r'\.', '', cleaned_name)  # Remove periods

                    # Split, reverse the first two words if possible, and rejoin
                    words = cleaned_name.strip().split()
                    if len(words) >= 2:
                        words[0], words[1] = words[1], words[0]
                    reversed_name = " ".join(words)

                    # Add the processed name to the list
                    processed_names.append(reversed_name)

                    # Search for the processed name in the second DataFrame (vendor_file)
                    vendor_file[ven_matched[0][0]] = vendor_file[ven_matched[0][0]].fillna('').astype(str).str.lower().str.strip()
                    reversed_name = reversed_name.lower().strip()

                    # matched_row = vendor_file[vendor_file[ven_matched[0][0]] == reversed_name]
                    # print('matched_row',matched_row)
                    # return

                    # New fuzzy match check
                    def normalize_name(name):
                        name = re.sub(r'[^\w\s]', '', name)  # Remove special characters
                        name = re.sub(r'\s+', ' ', name).strip()  # Remove extra spaces
                        name_words = name.lower().split()
                        return sorted(name_words)  # Sort words alphabetically for flexible matching

                    reversed_normalized = normalize_name(reversed_name)

                    matched_row = vendor_file[
                        vendor_file[ven_matched[0][0]].apply(lambda x: all(word in x.lower() for word in reversed_normalized))
                    ]


                    # matched_row = vendor_file[
                    #     vendor_file[ven_matched[0][0]].apply(lambda x: normalize_name(x) == reversed_normalized)
                    # ]


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


