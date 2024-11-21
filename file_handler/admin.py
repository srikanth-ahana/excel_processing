from django.contrib import admin
from .models import UploadedFile, ProcessedData, VendorTemplate, ArrivalTemplate


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'file2', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('file', 'file2')
    ordering = ('-uploaded_at',)


@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'guest_name', 'is_matched', 'commission', 'rate_amd', 'difference')
    list_filter = ('is_matched',)
    search_fields = ('guest_name',)
    ordering = ('guest_name',)
    readonly_fields = ('difference',)


@admin.register(VendorTemplate)
class VendorTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'template_name', 'guest_name', 'is_merged', 'arr_date_name', 'dept_date_name', 'arr_dept_date_name', 'amount_name')
    list_filter = ('is_merged',)
    search_fields = ('template_name', 'guest_name')
    ordering = ('template_name',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_merged:
            # Make certain fields readonly if is_merged is checked
            return self.readonly_fields + ('arr_date_name', 'dept_date_name')
        return self.readonly_fields


@admin.register(ArrivalTemplate)
class ArrivalTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_merged', 'arr_date_name', 'dept_date_name', 'arr_dept_date_name', 'rate_amt_name_name')
    list_filter = ('is_merged',)
    search_fields = ('name',)
    ordering = ('name',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_merged:
            # Make certain fields readonly if is_merged is checked
            return self.readonly_fields + ('arr_date_name', 'dept_date_name')
        return self.readonly_fields
