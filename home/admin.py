from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ContactInquiry, NewsletterSubscription, ContactMethod, 
    FAQ, Testimonial, Service, ContactLog
)
from django.utils import timezone

@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'practice_name', 'specialty', 'location', 
        'status', 'priority', 'submitted_at', 'days_since_submission'
    ]
    list_filter = [
        'status', 'priority', 'specialty', 'submitted_at', 
        'newsletter_subscription'
    ]
    search_fields = [
        'first_name', 'last_name', 'email', 'practice_name', 
        'location', 'message'
    ]
    readonly_fields = [
        'submitted_at', 'ip_address', 'user_agent', 'days_since_submission'
    ]
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Practice Information', {
            'fields': ('practice_name', 'specialty', 'location', 'current_website')
        }),
        ('Services & Project Details', {
            'fields': ('services_needed', 'budget_range', 'timeline')
        }),
        ('Message', {
            'fields': ('message', 'newsletter_subscription')
        }),
        ('Status & Follow-up', {
            'fields': ('status', 'priority', 'assigned_to', 'notes', 'last_contacted')
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_contacted', 'mark_as_qualified', 'assign_high_priority']
    
    def mark_as_contacted(self, request, queryset):
        queryset.update(status='contacted', last_contacted=timezone.now())
        self.message_user(request, f"{queryset.count()} inquiries marked as contacted.")
    mark_as_contacted.short_description = "Mark selected inquiries as contacted"
    
    def mark_as_qualified(self, request, queryset):
        queryset.update(status='qualified')
        self.message_user(request, f"{queryset.count()} inquiries marked as qualified.")
    mark_as_qualified.short_description = "Mark selected inquiries as qualified"
    
    def assign_high_priority(self, request, queryset):
        queryset.update(priority='high')
        self.message_user(request, f"{queryset.count()} inquiries assigned high priority.")
    assign_high_priority.short_description = "Assign high priority to selected inquiries"

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'source', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'source', 'subscribed_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['subscribed_at']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"

@admin.register(ContactMethod)
class ContactMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'value', 'is_primary', 'is_active', 'order']
    list_filter = ['type', 'is_primary', 'is_active']
    search_fields = ['name', 'value', 'description']
    list_editable = ['is_primary', 'is_active', 'order']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = [
        'doctor_name', 'practice_name', 'specialty', 'rating', 
        'is_featured', 'is_active', 'created_at'
    ]
    list_filter = ['is_featured', 'is_active', 'rating', 'specialty', 'created_at']
    search_fields = ['doctor_name', 'practice_name', 'specialty', 'testimonial_text']
    list_editable = ['is_featured', 'is_active', 'rating']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'base_price', 'price_period', 'is_featured', 
        'is_popular', 'is_active', 'order'
    ]
    list_filter = ['is_featured', 'is_popular', 'is_active', 'price_period']
    search_fields = ['name', 'description', 'short_description']
    list_editable = ['is_featured', 'is_popular', 'is_active', 'order']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'short_description', 'icon_class')
        }),
        ('Pricing', {
            'fields': ('base_price', 'price_period')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_popular', 'order', 'is_active')
        }),
    )

@admin.register(ContactLog)
class ContactLogAdmin(admin.ModelAdmin):
    list_display = [
        'inquiry_link', 'action', 'performed_by', 'performed_at', 'scheduled_date'
    ]
    list_filter = ['action', 'performed_at', 'scheduled_date']
    search_fields = ['inquiry__first_name', 'inquiry__last_name', 'description']
    readonly_fields = ['performed_at']
    date_hierarchy = 'performed_at'
    
    def inquiry_link(self, obj):
        if obj.inquiry:
            url = reverse('admin:home_contactinquiry_change', args=[obj.inquiry.id])
            return format_html('<a href="{}">{}</a>', url, obj.inquiry.full_name)
        return "N/A"
    inquiry_link.short_description = "Inquiry"
    inquiry_link.admin_order_field = 'inquiry__first_name'

# Customize admin site
admin.site.site_header = "DoctorConnect Administration"
admin.site.site_title = "DoctorConnect Admin"
admin.site.index_title = "Welcome to DoctorConnect Administration"
