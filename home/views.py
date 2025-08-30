from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
import json
import logging

from .models import (
    ContactInquiry, NewsletterSubscription, ContactMethod, 
    FAQ, Testimonial, Service, ContactLog
)
from .forms import (
    ContactInquiryForm, NewsletterSubscriptionForm, QuickContactForm
)

logger = logging.getLogger(__name__)

def home(request):
    """Home page view"""
    # Get featured testimonials
    featured_testimonials = Testimonial.objects.filter(
        is_active=True, 
        is_featured=True
    )[:2]
    
    # Get active services
    services = Service.objects.filter(is_active=True).order_by('order')
    
    # Get some statistics
    stats = {
        'total_doctors': ContactInquiry.objects.filter(status__in=['closed', 'negotiating']).count(),
        'total_inquiries': ContactInquiry.objects.count(),
        'active_subscriptions': NewsletterSubscription.objects.filter(is_active=True).count(),
    }
    
    context = {
        'featured_testimonials': featured_testimonials,
        'services': services,
        'stats': stats,
    }
    return render(request, 'home.html', context)

def about(request):
    """About page view"""
    # Get team statistics
    stats = {
        'years_experience': 5,
        'doctors_served': ContactInquiry.objects.filter(status__in=['closed', 'negotiating']).count(),
        'medical_specialties': ContactInquiry.objects.values('specialty').distinct().count(),
    }
    
    context = {
        'stats': stats,
    }
    return render(request, 'about.html', context)

def contact(request):
    """Contact page view"""
    # Get contact methods
    contact_methods = ContactMethod.objects.filter(is_active=True).order_by('order')
    
    # Get active FAQs
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    
    # Get office location info
    office_info = {
        'address': '123 Healthcare Avenue, Medical District, Healthcare City, HC 12345',
        'phone': '+1 (555) 123-4567',
        'email': 'hello@doctorconnect.com',
        'hours': 'Monday - Friday: 9:00 AM - 6:00 PM EST',
        'parking': 'Free parking available in our building',
    }
    
    context = {
        'contact_methods': contact_methods,
        'faqs': faqs,
        'office_info': office_info,
    }
    return render(request, 'contact.html', context)

@require_http_methods(["POST"])
def submit_contact_inquiry(request):
    """Handle contact form submission"""
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        
        if form.is_valid():
            try:
                # Create the contact inquiry
                inquiry = form.save(commit=False)
                
                # Get client IP and user agent
                inquiry.ip_address = get_client_ip(request)
                inquiry.user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                # Handle services selection
                services = form.cleaned_data.get('services_checkboxes', [])
                inquiry.services_needed = services
                
                # Save the inquiry
                inquiry.save()
                
                # Handle newsletter subscription if requested
                if form.cleaned_data.get('newsletter_subscription'):
                    NewsletterSubscription.objects.get_or_create(
                        email=inquiry.email,
                        defaults={
                            'first_name': inquiry.first_name,
                            'last_name': inquiry.last_name,
                            'source': 'contact-form'
                        }
                    )
                
                # Send confirmation email to the doctor
                send_doctor_confirmation_email(inquiry)
                
                # Send notification email to the team
                send_team_notification_email(inquiry)
                
                # Log the contact
                ContactLog.objects.create(
                    inquiry=inquiry,
                    action='form_submitted',
                    description=f'Contact form submitted via website',
                    performed_by='System',
                    performed_at=timezone.now()
                )
                
                # Return success response
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you! Your inquiry has been submitted successfully. We\'ll get back to you within 2 hours.',
                    'inquiry_id': inquiry.id
                })
                
            except Exception as e:
                logger.error(f"Error saving contact inquiry: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Sorry, there was an error submitting your inquiry. Please try again or contact us directly.'
                }, status=500)
        else:
            # Return form errors
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': errors
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@require_http_methods(["POST"])
def subscribe_newsletter(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        
        if form.is_valid():
            try:
                # Check if already subscribed
                email = form.cleaned_data['email']
                subscription, created = NewsletterSubscription.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': form.cleaned_data.get('first_name', ''),
                        'last_name': form.cleaned_data.get('last_name', ''),
                        'source': 'website'
                    }
                )
                
                if not created and subscription.is_active:
                    return JsonResponse({
                        'success': False,
                        'message': 'You are already subscribed to our newsletter.'
                    }, status=400)
                
                # Activate subscription if it was inactive
                if not subscription.is_active:
                    subscription.is_active = True
                    subscription.save()
                
                # Send welcome email
                send_newsletter_welcome_email(subscription)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing to our newsletter!'
                })
                
            except Exception as e:
                logger.error(f"Error subscribing to newsletter: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Sorry, there was an error subscribing you to our newsletter. Please try again.'
                }, status=500)
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': errors
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

@require_http_methods(["POST"])
def quick_contact(request):
    """Handle quick contact form"""
    if request.method == 'POST':
        form = QuickContactForm(request.POST)
        
        if form.is_valid():
            try:
                # Create a basic contact inquiry
                inquiry = ContactInquiry.objects.create(
                    first_name=form.cleaned_data['name'].split()[0] if form.cleaned_data['name'] else '',
                    last_name=' '.join(form.cleaned_data['name'].split()[1:]) if len(form.cleaned_data['name'].split()) > 1 else '',
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data.get('phone', ''),
                    practice_name='Quick Contact',
                    specialty='other',
                    location='Not specified',
                    message=form.cleaned_data['message'],
                    status='new',
                    priority='medium',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    notes=f"Quick contact form. Preferred contact method: {form.cleaned_data['contact_preference']}"
                )
                
                # Send notification email to team
                send_quick_contact_notification(inquiry, form.cleaned_data['contact_preference'])
                
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your message! We\'ll get back to you soon.'
                })
                
            except Exception as e:
                logger.error(f"Error processing quick contact: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Sorry, there was an error sending your message. Please try again.'
                }, status=500)
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': errors
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method.'
    }, status=405)

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def send_doctor_confirmation_email(inquiry):
    """Send confirmation email to the doctor"""
    try:
        subject = f"Thank you for your inquiry, Dr. {inquiry.last_name}!"
        
        context = {
            'inquiry': inquiry,
            'services': inquiry.services_needed,
        }
        
        html_message = render_to_string('emails/doctor_confirmation.html', context)
        plain_message = render_to_string('emails/doctor_confirmation.txt', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[inquiry.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL]
        )
        email.content_subtype = "html"
        email.send()
        
        logger.info(f"Confirmation email sent to {inquiry.email}")
        
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}")

def send_team_notification_email(inquiry):
    """Send notification email to the team"""
    try:
        subject = f"New Contact Inquiry: {inquiry.practice_name}"
        
        context = {
            'inquiry': inquiry,
            'services': inquiry.services_needed,
        }
        
        html_message = render_to_string('emails/team_notification.html', context)
        plain_message = render_to_string('emails/team_notification.txt', context)
        
        # Send to team email (you can configure this in settings)
        team_email = getattr(settings, 'TEAM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[team_email],
            reply_to=[inquiry.email]
        )
        email.content_subtype = "html"
        email.send()
        
        logger.info(f"Team notification email sent for inquiry {inquiry.id}")
        
    except Exception as e:
        logger.error(f"Error sending team notification email: {str(e)}")

def send_newsletter_welcome_email(subscription):
    """Send welcome email for newsletter subscription"""
    try:
        subject = "Welcome to DoctorConnect Newsletter!"
        
        context = {
            'subscription': subscription,
        }
        
        html_message = render_to_string('emails/newsletter_welcome.html', context)
        plain_message = render_to_string('emails/newsletter_welcome.txt', context)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[subscription.email]
        )
        email.content_subtype = "html"
        email.send()
        
        logger.info(f"Newsletter welcome email sent to {subscription.email}")
        
    except Exception as e:
        logger.error(f"Error sending newsletter welcome email: {str(e)}")

def send_quick_contact_notification(inquiry, contact_preference):
    """Send notification for quick contact form"""
    try:
        subject = f"Quick Contact: {inquiry.first_name} {inquiry.last_name}"
        
        context = {
            'inquiry': inquiry,
            'contact_preference': contact_preference,
        }
        
        html_message = render_to_string('emails/quick_contact_notification.html', context)
        plain_message = render_to_string('emails/quick_contact_notification.txt', context)
        
        team_email = getattr(settings, 'TEAM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[team_email],
            reply_to=[inquiry.email]
        )
        email.content_subtype = "html"
        email.send()
        
        logger.info(f"Quick contact notification sent for {inquiry.email}")
        
    except Exception as e:
        logger.error(f"Error sending quick contact notification: {str(e)}")

# API endpoints for AJAX requests
@csrf_exempt
def contact_api(request):
    """API endpoint for contact form submissions"""
    if request.method == 'POST':
        return submit_contact_inquiry(request)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def newsletter_api(request):
    """API endpoint for newsletter subscriptions"""
    if request.method == 'POST':
        return subscribe_newsletter(request)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def quick_contact_api(request):
    """API endpoint for quick contact form"""
    if request.method == 'POST':
        return quick_contact(request)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# Dashboard views for managing inquiries
def dashboard(request):
    """Dashboard for managing contact inquiries"""
    if not request.user.is_staff:
        return redirect('home')
    
    # Get recent inquiries
    recent_inquiries = ContactInquiry.objects.all().order_by('-submitted_at')[:10]
    
    # Get statistics
    stats = {
        'total_inquiries': ContactInquiry.objects.count(),
        'new_inquiries': ContactInquiry.objects.filter(status='new').count(),
        'contacted_inquiries': ContactInquiry.objects.filter(status='contacted').count(),
        'qualified_inquiries': ContactInquiry.objects.filter(status='qualified').count(),
        'closed_inquiries': ContactInquiry.objects.filter(status='closed').count(),
    }
    
    # Get inquiries by specialty
    specialty_stats = ContactInquiry.objects.values('specialty').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'recent_inquiries': recent_inquiries,
        'stats': stats,
        'specialty_stats': specialty_stats,
    }
    
    return render(request, 'dashboard.html', context)

def inquiry_detail(request, inquiry_id):
    """Detail view for a specific inquiry"""
    if not request.user.is_staff:
        return redirect('home')
    
    inquiry = get_object_or_404(ContactInquiry, id=inquiry_id)
    contact_logs = inquiry.contact_logs.all().order_by('-performed_at')
    
    context = {
        'inquiry': inquiry,
        'contact_logs': contact_logs,
    }
    
    return render(request, 'inquiry_detail.html', context)
